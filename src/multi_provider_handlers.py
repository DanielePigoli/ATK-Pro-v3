import os
import re
import json
import base64
import logging
import time
from key_manager import (
    get_provider_base_url,
    require_provider_default_host,
    require_provider_default_model,
)

try:
    import google.generativeai as genai
    from google.generativeai.types import GenerationConfig
except ImportError:
    genai = None

class AIProviderHandler:
    def __init__(self, provider, api_key):
        self.provider = provider
        self.api_key = api_key

    def set_key(self, key):
        self.api_key = key

    def extract_genealogy(self, prompt, image_path=None, model=None):
        raise NotImplementedError
        
    def _cleanup_json_response(self, text):
        """Pulisce la risposta IA per estrarre un JSON valido, riparando errori comuni."""
        import re
        if not text: return "{}"
        
        # 1. Estrazione del blocco tra graffe
        match = re.search(r"(\{.*\})", text, re.DOTALL)
        clean = match.group(1) if match else text.strip()
        
        # 2. Rimozione commenti in stile C/JS se presenti
        clean = re.sub(r'//.*?\n|/\*.*?\*/', '', clean, flags=re.S)
        
        # 3. Riparazione virgole finali prima di chiusura graffa/quadra
        clean = re.sub(r',\s*\}', '}', clean)
        clean = re.sub(r',\s*\]', ']', clean)
        
        # 4. Sincro v15.7: Auto-Close per troncamenti IA
        open_braces = clean.count('{') - clean.count('}')
        open_brackets = clean.count('[') - clean.count(']')
        
        # Se c'è una chiave appesa come "field": (senza valore)
        if clean.strip().endswith(':'):
             clean += ' ""'
        
        # Chiudi nell'ordine inverso
        if open_brackets > 0: clean += ']' * open_brackets
        if open_braces > 0: clean += '}' * open_braces
        
        return clean

    def _parse_markdown_table(self, text):
        """Converte una tabella Markdown indicizzata (Num:Val) in JSON rigenerando le chiavi corrette."""
        rows = []
        lines = [l.strip() for l in text.split('\n') if l.strip().startswith('|')]
        if len(lines) < 2: return []
        
        data_start = 0
        for i, line in enumerate(lines):
            if '---' in line:
                data_start = i + 1
                break
        
        actual_data = lines[data_start:]
        for line in actual_data:
            line_content = line.strip('|')
            cols = [c.strip() for c in line_content.split('|')]
            row_dict = {}
            for col_idx, raw_val in enumerate(cols):
                val = raw_val
                if ':' in raw_val:
                    parts = raw_val.split(':', 1)
                    idx_str = parts[0].strip()
                    if idx_str.isdigit():
                        val = parts[1].strip()
                        target_idx = idx_str
                    else: target_idx = str(col_idx + 1)
                else: target_idx = str(col_idx + 1)
                row_dict[target_idx] = val
            
            if any(v for k, v in row_dict.items() if v):
                rows.append(row_dict)
        return rows

    def _sanitize_json_text(self, text: str) -> str:
        """Ripara errori comuni (es. virgolette triple per segni di ripetizione)."""
        text = re.sub(r'":\s*["\s]{2,}(?=[,}\s])', '": "\\""', text)
        return text

    def _parse_rows_from_text(self, raw_text: str) -> list:
        """Parser unificato: estrae lista di righe da JSON o tabella Markdown."""
        def find_rows(obj):
            if isinstance(obj, list): return obj
            if isinstance(obj, dict):
                if "righe" in obj: return obj["righe"]
                for k, v in obj.items():
                    if isinstance(v, list) and len(v) > 0: return v
                if '3' in obj or 3 in obj: return [obj]
                first_val = next(iter(obj.values()), None)
                if isinstance(first_val, dict): return list(obj.values())
            return []

        sanitized = self._sanitize_json_text(raw_text)

        arr_match = re.search(r"\[.*\]", sanitized, re.DOTALL)
        if arr_match:
            try:
                data = json.loads(arr_match.group(0))
                rows = find_rows(data)
                if rows:
                    return rows
            except Exception:
                pass

        obj_match = re.search(r"\{.*\}", sanitized, re.DOTALL)
        if obj_match:
            try:
                data = json.loads(obj_match.group(0))
                rows = find_rows(data)
                if rows:
                    return rows
            except Exception:
                pass

        return self._parse_markdown_table(raw_text)

class GeminiHandler(AIProviderHandler):
    """Sincronia v15.3: Implementazione Ufficiale Google-GenerativeAI"""
    def _get_available_models(self):
        """Interroga dinamicamente l'account e seleziona i 2 migliori per stabilità e quota."""
        try:
            genai.configure(api_key=self.api_key)
            models = genai.list_models()
            discovery = []
            # Puntiamo ai modelli che hanno quote più ampie o sono i più recenti
            preference = ['flash-lite-latest', '2.0-flash', 'flash-latest']
            
            discovered_names = [m.name for m in models if "generateContent" in m.supported_generation_methods]
            
            for pref in preference:
                for dn in discovered_names:
                    if pref in dn.lower():
                        discovery.append(dn)
                        break
                if len(discovery) >= 2: break
                
            return discovery if discovery else ['models/gemini-1.5-flash']
        except Exception as e:
            logging.warning(f"[AUTO-DISCOVERY] Fallito: {e}")
        return ['models/gemini-1.5-flash', 'models/gemini-flash-latest']

    def _extract_text_only_gemini(self, prompt: str, debug_dir=None) -> list:
        """
        PIPELINE DUE FASI — MODALITÀ TESTO: chiamata diretta a Gemini senza
        pipeline immagine.
        """
        import time
        from ai_utils import get_best_gemini_model
        genai.configure(api_key=self.api_key)

        # Usa ai_utils per trovare i modelli reali disponibili per questa chiave
        # invece di hardcodare modelli che potrebbero avere limit: 0 sul free tier
        target_models = [
            get_best_gemini_model(self.api_key, preferred="pro"),
            get_best_gemini_model(self.api_key, preferred="flash")
        ]
        
        # Rimuovi duplicati mantenendo l'ordine
        seen = set()
        target_models = [m for m in target_models if m not in seen and not seen.add(m)]
        # Aggiungi 'models/' per l'SDK se non presente
        target_models = [m if m.startswith('models/') else f'models/{m}' for m in target_models]

        for m_name in target_models:
            try:
                logging.info(f"[TEXT-MODE] Chiamata testo-only con {m_name}...")
                vision_model = genai.GenerativeModel(model_name=m_name)
                response = vision_model.generate_content(
                    [prompt],
                    generation_config=GenerationConfig(temperature=0.0, max_output_tokens=65536)
                )
                if response.text:
                    raw_text = response.text
                    if debug_dir:
                        d_path = os.path.join(debug_dir, "DIAGNOSTICA_trascrizione_IA_TESTO.md")
                        try:
                            with open(d_path, "w", encoding="utf-8") as f:
                                f.write(raw_text)
                        except Exception:
                            pass
                    rows = self._parse_rows_from_text(raw_text)
                    logging.info(f"[TEXT-MODE] Righe estratte: {len(rows)}")
                    return rows
            except Exception as e:
                logging.warning(f"[TEXT-MODE] Errore con {m_name}: {e}")
                err_lower = str(e).lower()
                if "429" in err_lower or "quota" in err_lower or "limit: 0" in err_lower:
                    # Quota esaurita su questo modello: prova il prossimo della lista
                    # (es. gemini-2.0-flash dopo gemini-2.5-pro). Se anche flash fallisce
                    # l'eccezione finale innescherà la rotazione alla chiave successiva.
                    logging.info(f"[TEXT-MODE] Quota esaurita su {m_name}, provo modello successivo...")
                    continue
                continue

        raise Exception(f"Tutti i modelli Gemini esauriti per questa chiave (text-only).")

    def extract_genealogy(self, prompt, image_path=None, model=None, debug_dir=None):
        if not genai:
            raise ImportError("La libreria 'google-generativeai' non è installata.")

        # PIPELINE DUE FASI: se non c'è immagine, usa il path testo-only
        if not image_path or not os.path.exists(str(image_path or '')):
            return self._extract_text_only_gemini(prompt, debug_dir)

        from PIL import Image, ImageEnhance, ImageFilter
        import io
        import time 
        
        available_models = self._get_available_models()
        genai.configure(api_key=self.api_key)

        slices = []
        if image_path and os.path.exists(image_path):
            with Image.open(image_path) as img:
                if img.mode != "RGB": img = img.convert("RGB")
                
                # Sincro v30.0: FILTRAZIONE OTTICA AVANZATA (Contrast + UnsharpMask)
                enhancer = ImageEnhance.Contrast(img)
                img = enhancer.enhance(1.8) # Contrasto ancora più marcato
                img = img.filter(ImageFilter.UnsharpMask(radius=2, percent=150, threshold=3)) # Definisce i bordi dell'inchiostro
                img = img.filter(ImageFilter.SHARPEN)
                
                w, h = img.size
                # Sincro v48.0: VISTA SPLIT (2 Strisce) - Ultra Risoluzione
                # Usiamo solo 2 strisce (Top/Bottom) con ampia sovrapposizione (20%)
                # per garantire che nessuna riga venga spezzata e riduciamo le chiamate API.
                header_h = int(h * 0.12) # Circa il 12% superiore contiene le intestazioni
                header_img = img.crop((0, 0, w, header_h))
                
                strips_configs = [
                    ("TOP", (0, 0, w, int(h * 0.60))),
                    ("BOTTOM", (0, int(h * 0.40), w, h))
                ]

                for label, box in strips_configs:
                    tile = img.crop(box)
                    
                    # Sincro v48.2: HEADER STITCHING per la striscia BOTTOM
                    # Se stiamo lavorando sulla parte bassa, incolliamo l'intestazione in cima
                    # per garantire che l'IA veda sempre le etichette dello Stato Civile (7-12).
                    if label == "BOTTOM":
                        combined = Image.new('RGB', (w, tile.height + header_h))
                        combined.paste(header_img, (0, 0))
                        combined.paste(tile, (0, header_h))
                        tile = combined

                    # Sincro v48.0: Ridimensionamento Forzato a 4000px di altezza
                    target_h = 4000
                    curr_w, curr_h = tile.size
                    scale = target_h / curr_h
                    target_w = int(curr_w * scale)
                    tile = tile.resize((target_w, target_h), Image.LANCZOS)
                    
                    img_byte_arr = io.BytesIO()
                    tile.save(img_byte_arr, format='JPEG', quality=95)
                    slices.append((label, Image.open(img_byte_arr)))

        # Eseguiamo le passate (Strisce)
        all_quadrant_rows = []
        
        # Priorità: Pro migliore → Pro precedente → Flash (fallback quota free tier)
        from ai_utils import get_best_gemini_model
        best_pro   = get_best_gemini_model(self.api_key, preferred="pro")
        best_flash = get_best_gemini_model(self.api_key, preferred="flash")
        _seen = set()
        target_models = []
        for _m in [best_pro, "models/gemini-2.5-pro", best_flash, "models/gemini-2.0-flash"]:
            _m = _m if _m.startswith('models/') else f'models/{_m}'
            if _m not in _seen:
                _seen.add(_m)
                target_models.append(_m)
        
        # Log di verifica per debugging
        logging.info(f"[SINCRO] Modelli PRO certificati in prova: {target_models}")

        for label, tile in slices:
            side_prompt = f"LAVORA SULLA {label}. COLONNE 1-20 (Intero rigo).\nREGOLE TAGLI: Trascrivi *SOLO* le righe perfettamente visibili e intere. IGNORA SCORBUTICAMENTE qualsiasi riga il cui testo è anche solo parzialmente tagliato dal bordo superiore o inferiore. Niente deduzioni. {prompt}"
            
            success = False
            for m_name in target_models:
                try:
                    # Turbo Mode v36.8: Rimossa pausa di 5s (Billing attivo) per evitare timeout GUI
                    logging.info(f"[SINCRONIA] {label} con {m_name} (MODALITÀ TURBO PRO - v36.8)...")
                    vision_model = genai.GenerativeModel(model_name=m_name)
                    # Temperatura 0.0 (Zero Assoluto) e Token Espansi per file completi (v46.1)
                    response = vision_model.generate_content([tile, side_prompt], 
                                                           generation_config=GenerationConfig(temperature=0.0, max_output_tokens=65536))
                    if response.text:
                        raw_text = response.text
                        f_name = os.path.join(debug_dir if debug_dir else os.getcwd(), f"DIAGNOSTICA_trascrizione_IA_{label}.md")
                        with open(f_name, "w", encoding="utf-8") as df:
                            df.write(raw_text)

                        q_rows = self._parse_rows_from_text(raw_text)
                        all_quadrant_rows.extend(q_rows)
                        success = True
                        break
                except Exception as e:
                    logging.warning(f"Errore {label} su {m_name}: {e}")
                    # Se il PRO fallisce per quota, aspettiamo di più e riproviamo CON LO STESSO MODELLO
                    if "429" in str(e) or "503" in str(e) or "quota" in str(e).lower():
                        logging.info("[SINCRONIA] Errore rete/quota. Pausa lunga (20s) e riprovo...")
                        time.sleep(20)
                        # Qui il ciclo for riproverà il modello successivo, ma se è l'unico 'pro' ripeterà il tentativo
                    continue
            if not success: raise Exception(f"Impossibile elaborare {label} con modelli di classe PRO.")

        # UNIONE SEQUENZIALE PER IDENTITÀ (v48.0 - Persona_Nr Key)
        merged_rows = []
        master_map = {}
        last_valid_p_nr = 0
        
        try:
            for row in all_quadrant_rows:
                if not isinstance(row, dict): continue
                
                # Estrazione e pulizia del progressivo (Colonna 3)
                raw_p_id = str(row.get('3', '')).strip()
                import re
                m = re.search(r'(\d+)', raw_p_id)
                
                if m:
                    p_id = m.group(1)
                    last_valid_p_nr = int(p_id)
                else:
                    # Logica suggerita dall'utente: se manca, è il precedente + 1
                    last_valid_p_nr += 1
                    p_id = str(last_valid_p_nr)
                    row['3'] = p_id 
                
                if p_id not in master_map:
                    master_map[p_id] = row
                else:
                    # Fusione dati: riempiamo i buchi del record esistente (es. se nella prima passata era troncato)
                    for k, v in row.items():
                        v_str = str(v).strip()
                        current_val = str(master_map[p_id].get(k, '')).strip()
                        if v_str and not current_val:
                            master_map[p_id][k] = v_str
                        # Se il master ha un segno di ripetizione ma il nuovo ha il testo completo, aggiorna
                        elif v_str and current_val in ['"', '”', '“'] and v_str not in ['"', '”', '“']:
                            master_map[p_id][k] = v_str

            # Trasformiamo la mappa in lista ordinata per ID
            sorted_keys = sorted(master_map.keys(), key=lambda x: int(x))
            merged_rows = [master_map[k] for k in sorted_keys]
            
            logging.info(f"[SINCRONIA] Merge completato (v48.0). Individui unici: {len(merged_rows)}")
            
            # SALVATAGGIO DIAGNOSTICA UNIFICATA (Spostato prima del return)
            try:
                d_path = debug_dir if debug_dir else os.getcwd()
                diag_file = os.path.join(d_path, "DIAGNOSTICA_tabella_unita.md")
                with open(diag_file, "w", encoding="utf-8") as f:
                    f.write("# DIAGNOSTICA TABELLA UNITA (Merge v48.0)\n\n")
                    json.dump(merged_rows, f, indent=2)
                logging.debug(f"[SINCRONIA] Diagnostica unita salvata in: {diag_file}")
            except Exception as de:
                logging.warning(f"Impossibile salvare diagnostica unita: {de}")

            return merged_rows
        except Exception as e:
            logging.error(f"[SINCRONIA] Errore critico durante il merge: {str(e)}. Salvo i dati grezzi.")
            # Fallback estremo: restituisci i dati non filtrati per non perdere nulla
            return [r for r in all_quadrant_rows if isinstance(r, dict)]
        
        raise Exception("Errore critico durante lo split visivo.")

class OpenAIHandler(AIProviderHandler):
    def extract_genealogy(self, prompt, image_path=None, model=None, debug_dir=None):
        from openai import OpenAI
        if not model:
            model = require_provider_default_model("OpenAI", "ai_search")
        client = OpenAI(api_key=self.api_key)
        content = [{"type": "text", "text": prompt}]
        if image_path and os.path.exists(image_path):
            ext = os.path.splitext(image_path)[1].lower()
            if ext in (".tif", ".tiff"):
                try:
                    from PIL import Image
                    import io
                    with Image.open(image_path) as im:
                        buf = io.BytesIO()
                        im.convert("RGB").save(buf, format="JPEG", quality=90)
                        b64 = base64.b64encode(buf.getvalue()).decode("utf-8")
                except Exception:
                    b64 = None
            else:
                with open(image_path, "rb") as f:
                    b64 = base64.b64encode(f.read()).decode("utf-8")
            if b64:
                content.insert(0, {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64}"}})
        try:
            response = client.chat.completions.create(
                model=model,
                max_tokens=16000,
                messages=[{"role": "user", "content": content}]
            )
            raw_text = response.choices[0].message.content
            if debug_dir:
                d_path = os.path.join(debug_dir, "DIAGNOSTICA_trascrizione_IA_OPENAI.md")
                try:
                    with open(d_path, "w", encoding="utf-8") as f:
                        f.write(raw_text)
                except Exception:
                    pass
            rows = self._parse_rows_from_text(raw_text)
            logging.info(f"[OpenAI] Righe estratte: {len(rows)}")
            return rows
        except Exception as e:
            raise e

class ClaudeHandler(AIProviderHandler):
    def extract_genealogy(self, prompt, image_path=None, model=None, debug_dir=None):
        from anthropic import Anthropic
        if not model:
            model = require_provider_default_model("Claude", "ai_search")
        client = Anthropic(api_key=self.api_key)
        content = []
        if image_path and os.path.exists(image_path):
            ext = os.path.splitext(image_path)[1].lower()
            media_type_map = {
                ".jpg": "image/jpeg", ".jpeg": "image/jpeg",
                ".png": "image/png", ".gif": "image/gif",
                ".webp": "image/webp", ".tif": "image/jpeg",
                ".tiff": "image/jpeg",
            }
            media_type = media_type_map.get(ext, "image/jpeg")
            # TIF non supportato direttamente: converti in JPEG in memoria
            if ext in (".tif", ".tiff"):
                try:
                    from PIL import Image
                    import io
                    with Image.open(image_path) as im:
                        buf = io.BytesIO()
                        im.convert("RGB").save(buf, format="JPEG", quality=90)
                        img_data = base64.b64encode(buf.getvalue()).decode("utf-8")
                except Exception:
                    img_data = None
            else:
                with open(image_path, "rb") as f:
                    img_data = base64.b64encode(f.read()).decode("utf-8")
            if img_data:
                content.append({
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": media_type,
                        "data": img_data,
                    }
                })
        content.append({"type": "text", "text": prompt})
        try:
            with client.messages.stream(
                model=model,
                max_tokens=32000,
                messages=[{"role": "user", "content": content}]
            ) as stream:
                raw_text = stream.get_final_text()
            if debug_dir:
                d_path = os.path.join(debug_dir, "DIAGNOSTICA_trascrizione_IA_CLAUDE.md")
                try:
                    with open(d_path, "w", encoding="utf-8") as f:
                        f.write(raw_text)
                except Exception:
                    pass
            rows = self._parse_rows_from_text(raw_text)
            logging.info(f"[Claude] Righe estratte: {len(rows)}")
            return rows
        except Exception as e:
            raise e

class OpenAICompatibleHandler(AIProviderHandler):
    """Handler generico per provider con API compatibile OpenAI (Mistral, Groq, DeepSeek, xAI)."""
    _NO_VISION = {"DeepSeek"}

    def extract_genealogy(self, prompt, image_path=None, model=None, debug_dir=None):
        from openai import OpenAI
        base_url = get_provider_base_url(self.provider)
        if not model:
            model = require_provider_default_model(self.provider, "ai_search")
        client = OpenAI(api_key=self.api_key, base_url=base_url)
        content = [{"type": "text", "text": prompt}]
        if image_path and os.path.exists(image_path) and self.provider not in self._NO_VISION:
            ext = os.path.splitext(image_path)[1].lower()
            if ext in (".tif", ".tiff"):
                try:
                    from PIL import Image
                    import io
                    with Image.open(image_path) as im:
                        buf = io.BytesIO()
                        im.convert("RGB").save(buf, format="JPEG", quality=90)
                        b64 = base64.b64encode(buf.getvalue()).decode("utf-8")
                except Exception:
                    b64 = None
            else:
                with open(image_path, "rb") as f:
                    b64 = base64.b64encode(f.read()).decode("utf-8")
            if b64:
                content.insert(0, {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64}"}})
        try:
            response = client.chat.completions.create(
                model=model,
                max_tokens=16000,
                messages=[{"role": "user", "content": content}]
            )
            raw_text = response.choices[0].message.content
            if debug_dir:
                d_path = os.path.join(debug_dir, f"DIAGNOSTICA_trascrizione_IA_{self.provider}.md")
                try:
                    with open(d_path, "w", encoding="utf-8") as f:
                        f.write(raw_text)
                except Exception:
                    pass
            rows = self._parse_rows_from_text(raw_text)
            logging.info(f"[{self.provider}] Righe estratte: {len(rows)}")
            return rows
        except Exception as e:
            raise e


class OllamaHandler(AIProviderHandler):
    """Handler per Ollama — modelli locali, nessuna API key.
    api_key viene riutilizzato per l'host (es. http://localhost:11434).
    """

    def extract_genealogy(self, prompt, image_path=None, model=None, debug_dir=None):
        from openai import OpenAI
        default_host = require_provider_default_host("Ollama")
        host = self.api_key.strip() if self.api_key and self.api_key.strip().startswith("http") else default_host
        base_url = host.rstrip("/") + "/v1"
        if not model:
            model = require_provider_default_model("Ollama", "ai_search")
        # Ollama accetta qualsiasi stringa come api_key
        client = OpenAI(api_key="ollama", base_url=base_url)
        content = [{"type": "text", "text": prompt}]
        if image_path and os.path.exists(image_path):
            ext = os.path.splitext(image_path)[1].lower()
            if ext in (".tif", ".tiff"):
                try:
                    from PIL import Image
                    import io
                    with Image.open(image_path) as im:
                        buf = io.BytesIO()
                        im.convert("RGB").save(buf, format="JPEG", quality=90)
                        b64 = base64.b64encode(buf.getvalue()).decode("utf-8")
                except Exception:
                    b64 = None
            else:
                with open(image_path, "rb") as f:
                    b64 = base64.b64encode(f.read()).decode("utf-8")
            if b64:
                content.insert(0, {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64}"}})
        try:
            response = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": content}]
            )
            raw_text = response.choices[0].message.content
            if debug_dir:
                d_path = os.path.join(debug_dir, "DIAGNOSTICA_trascrizione_IA_OLLAMA.md")
                try:
                    with open(d_path, "w", encoding="utf-8") as f:
                        f.write(raw_text)
                except Exception:
                    pass
            rows = self._parse_rows_from_text(raw_text)
            logging.info(f"[Ollama:{model}] Righe estratte: {len(rows)}")
            return rows
        except Exception as e:
            raise e


class HuggingFaceHandler(AIProviderHandler):
    """Handler per Hugging Face Inference API (endpoint OpenAI-compatibile v1).
    Supporta modelli vision come Qwen2.5-VL, LLaVA, TrOCR (solo testo).
    api_key = HF token (hf_...).
    """
    # Modelli che non supportano vision — fallback a testo
    _NO_VISION_PREFIXES = ("microsoft/trocr", "facebook/bart", "t5-")

    def _is_vision_model(self, model: str) -> bool:
        ml = model.lower()
        return not any(ml.startswith(p) for p in self._NO_VISION_PREFIXES)

    def extract_genealogy(self, prompt, image_path=None, model=None, debug_dir=None):
        from openai import OpenAI
        if not model:
            model = require_provider_default_model("HuggingFace", "ai_search")
        client = OpenAI(api_key=self.api_key, base_url=get_provider_base_url("HuggingFace"))
        content = [{"type": "text", "text": prompt}]
        if image_path and os.path.exists(image_path) and self._is_vision_model(model):
            ext = os.path.splitext(image_path)[1].lower()
            if ext in (".tif", ".tiff"):
                try:
                    from PIL import Image
                    import io
                    with Image.open(image_path) as im:
                        buf = io.BytesIO()
                        im.convert("RGB").save(buf, format="JPEG", quality=90)
                        b64 = base64.b64encode(buf.getvalue()).decode("utf-8")
                except Exception:
                    b64 = None
            else:
                with open(image_path, "rb") as f:
                    b64 = base64.b64encode(f.read()).decode("utf-8")
            if b64:
                content.insert(0, {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64}"}})
        try:
            response = client.chat.completions.create(
                model=model,
                max_tokens=8192,
                messages=[{"role": "user", "content": content}]
            )
            raw_text = response.choices[0].message.content
            if debug_dir:
                d_path = os.path.join(debug_dir, "DIAGNOSTICA_trascrizione_IA_HUGGINGFACE.md")
                try:
                    with open(d_path, "w", encoding="utf-8") as f:
                        f.write(raw_text)
                except Exception:
                    pass
            rows = self._parse_rows_from_text(raw_text)
            logging.info(f"[HuggingFace:{model}] Righe estratte: {len(rows)}")
            return rows
        except Exception as e:
            raise e


def get_handler(provider, api_key):
    if provider == "OpenAI":   return OpenAIHandler(provider, api_key)
    if provider == "Claude":   return ClaudeHandler(provider, api_key)
    if provider == "Ollama":   return OllamaHandler(provider, api_key)
    if provider == "HuggingFace": return HuggingFaceHandler(provider, api_key)
    if provider in ("Mistral", "Groq", "DeepSeek", "xAI"): return OpenAICompatibleHandler(provider, api_key)
    return GeminiHandler("Gemini", api_key)
