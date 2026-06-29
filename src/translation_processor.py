from PySide6.QtCore import QThread, Signal
import logging
try:
    import google.generativeai as genai
except ImportError:
    genai = None
import openai
import os
from key_manager import missing_provider_credentials_message

class TranslationWorker(QThread):
    finished = Signal(bool, str)

    def __init__(self, provider, api_key, source_text, target_lang_autonym, context_info="", custom_model=None):
        super().__init__()
        self.provider = provider
        self.source_text = source_text
        self.target_lang = target_lang_autonym
        self.context_info = context_info
        self.custom_model = custom_model

        # --- Gestione chiavi: Cassaforte > campo manuale ---
        from key_manager import KeyManager
        km = KeyManager()
        km_keys = km.get_all_keys(provider)
        if km_keys:
            self.api_keys = km_keys
            logging.info(f"[TRANS] Cassaforte: {len(km_keys)} chiave/i per {provider}.")
        elif self.provider == "Ollama":
            self.api_keys = ["http://localhost:11434"]
            logging.info("[TRANS] Ollama locale: host predefinito in uso.")
        elif api_key:
            self.api_keys = [api_key]
        else:
            self.api_keys = []

        self.openai_client = None
        self.anthropic_client = None

    def run(self):
        if not self.api_keys:
            self.finished.emit(False, missing_provider_credentials_message(self.provider))
            return
        try:
            if not self.source_text.strip():
                raise ValueError("Nessun testo sorgente fornito per la traduzione.")

            prompt = self._build_prompt()
            translated_text = ""
            last_error = None

            for slot, key in enumerate(self.api_keys, start=1):
                try:
                    if self.provider == "Gemini":
                        if self.custom_model:
                            model_name = self.custom_model
                        else:
                            from ai_utils import get_best_gemini_model
                            model_name = get_best_gemini_model(key, preferred="flash")
                        genai.configure(api_key=key)
                        gemini_model = genai.GenerativeModel(model_name)
                        logging.info(
                            "[TRANS] Uso modello %s con chiave slot %s/%s.",
                            model_name,
                            slot,
                            len(self.api_keys),
                        )
                        translated_text = self._call_gemini_model(gemini_model, prompt)
                    elif self.provider == "OpenAI":
                        self.openai_client = openai.OpenAI(api_key=key)
                        translated_text = self._call_openai(prompt, model=self.custom_model)
                    elif self.provider == "Claude":
                        import anthropic
                        self.anthropic_client = anthropic.Anthropic(api_key=key)
                        translated_text = self._call_claude(prompt, model=self.custom_model)
                    elif self.provider == "Mistral":
                        translated_text = self._call_openai_compat(key, prompt, "https://api.mistral.ai/v1", self.custom_model or "mistral-large-latest")
                    elif self.provider == "Groq":
                        translated_text = self._call_openai_compat(key, prompt, "https://api.groq.com/openai/v1", self.custom_model or "llama-3.3-70b-versatile")
                    elif self.provider == "DeepSeek":
                        translated_text = self._call_openai_compat(key, prompt, "https://api.deepseek.com", self.custom_model or "deepseek-chat")
                    elif self.provider == "xAI":
                        translated_text = self._call_openai_compat(key, prompt, "https://api.x.ai/v1", self.custom_model or "grok-3-mini")
                    elif self.provider == "Ollama":
                        host = key.strip() if key.strip().startswith("http") else "http://localhost:11434"
                        translated_text = self._call_openai_compat("ollama", prompt, host.rstrip("/") + "/v1", self.custom_model or "llama3.2")
                    elif self.provider == "HuggingFace":
                        translated_text = self._call_openai_compat(key, prompt, "https://api-inference.huggingface.co/v1/", self.custom_model or "Qwen/Qwen2.5-72B-Instruct")
                    else:
                        raise ValueError(f"Provider non supportato: {self.provider}")
                    self.finished.emit(True, translated_text.strip())
                    return
                except Exception as e:
                    err_str = str(e).lower()
                    is_quota = any(k in err_str for k in ["429", "quota", "resource_exhausted", "rate"])
                    last_error = e
                    if is_quota:
                        logging.warning(
                            "[TRANS] Quota esaurita sullo slot chiave %s/%s. Provo prossima chiave...",
                            slot,
                            len(self.api_keys),
                        )
                        continue
                    else:
                        raise e

            raise Exception(f"Tutte le chiavi esaurite. Ultimo errore: {last_error}")

        except Exception as e:
            err_str = str(e)
            if "API_KEY" in err_str or "unauthorized" in err_str.lower() or "invalid" in err_str.lower():
                err_str = "API Key non valida, mancante o disabilitata per la fatturazione."
            elif "quota" in err_str.lower() or "429" in err_str:
                err_str = "Tutte le chiavi hanno superato il limite. Attendi e riprova."
            elif "504" in err_str or "timeout" in err_str.lower():
                err_str = "Connessione scaduta (Timeout). Il server era troppo occupato."
            self.finished.emit(False, f"Errore durante la traduzione ({self.provider}): {err_str}")

    def _build_prompt(self):
        base_prompt = (
            f"Sei uno specialista accademico di paleografia e genealogia.\n"
            f"Traduci responsabilmente il seguente documento storico nella lingua target: '{self.target_lang}'.\n"
            "Non omettere periodi, mantieni la formattazione a righe originaria se possibile e non aggiungere saluti formali."
        )
        if self.context_info.strip():
            base_prompt += f"\n\nATTTENZIONE AL CONTESTO STORICO/GLOSSARIO SPECIFICO:\n{self.context_info.strip()}\n"
            
        base_prompt += f"\n\nTESTO SORGENTE DA TRADURRE:\n{self.source_text}"
        return base_prompt

    def _call_gemini(self, prompt):
        """Mantenuto per compatibilità con vecchio codice."""
        if not self.api_keys:
            raise Exception("Nessuna chiave disponibile")
        from ai_utils import get_best_gemini_model
        key = self.api_keys[0]
        model_name = get_best_gemini_model(key, preferred="flash")
        genai.configure(api_key=key)
        model = genai.GenerativeModel(model_name)
        return self._call_gemini_model(model, prompt)

    def _call_gemini_model(self, model, prompt):
        response = model.generate_content(prompt, request_options={"timeout": 600})
        return response.text

    def _call_openai(self, prompt, model=None):
        if not model: model = "gpt-4o"
        response = self.openai_client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            timeout=600
        )
        return response.choices[0].message.content

    def _call_claude(self, prompt, model=None):
        if not model: model = "claude-3-5-sonnet-latest"
        with self.anthropic_client.messages.stream(
            model=model,
            max_tokens=8192,
            messages=[{"role": "user", "content": prompt}],
            timeout=600
        ) as stream:
            return stream.get_final_text()

    def _call_openai_compat(self, api_key, prompt, base_url, model):
        """Chiamata testo-only verso qualsiasi endpoint OpenAI-compatibile."""
        from openai import OpenAI
        client = OpenAI(api_key=api_key, base_url=base_url)
        response = client.chat.completions.create(
            model=model,
            max_tokens=8192,
            messages=[{"role": "user", "content": prompt}],
            timeout=600
        )
        return response.choices[0].message.content
