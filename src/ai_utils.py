import os
import re
import logging
try:
    import google.generativeai as genai
except ImportError:
    genai = None
from key_manager import KeyManager

def _model_capability_score(name: str) -> tuple:
    """
    Ritorna uno score (versione_major, versione_minor, tier) per ordinare i modelli
    per capacità decrescente. Usato come chiave di sort (più alto = migliore).
    Tier: pro=3, flash=2, flash-lite=1, altri=0
    """
    # Estrae versione dal nome: es. "gemini-2.5-pro-preview" → (2, 5), "gemini-3-flash" → (3, 0)
    m = re.search(r'gemini-(\d+)(?:\.(\d+))?', name)
    major = int(m.group(1)) if m else 0
    minor = int(m.group(2)) if m and m.group(2) else 0

    name_low = name.lower()
    if 'flash-lite' in name_low or 'flash_lite' in name_low:
        tier = 1
    elif 'flash' in name_low:
        tier = 2
    elif 'pro' in name_low:
        tier = 3
    else:
        tier = 0

    return (major, minor, tier)


def get_best_gemini_model(api_key, preferred="flash"):
    """
    Scansiona i modelli disponibili per la chiave fornita e ritorna il migliore
    per capacità (versione più alta + tier più alto).

    preferred="pro"   → privilegia modelli pro (include anche preview perché i pro
                        Gemini sono attualmente in preview)
    preferred="flash" → privilegia modelli flash non-lite; usa lite solo come ultimo
                        fallback
    preferred="best"  → restituisce il modello con score più alto in assoluto
    """
    try:
        if genai is None:
            raise ImportError("google-generativeai non installato")
        genai.configure(api_key=api_key)
        models = genai.list_models()

        valid = []
        for m in models:
            if 'generateContent' not in m.supported_generation_methods:
                continue
            name = m.name.replace('models/', '')
            name_low = name.lower()
            # Supporta modelli Gemini con o senza cifre decimali (es. gemini-2.5, gemini-3)
            # Esclude Gemma, Lyria, robotics, nano-banana, deep-research, ecc.
            if not re.search(r'^gemini-\d+', name_low):
                continue
            
            # Estrae la versione major per gestire i preview
            v_match = re.search(r'gemini-(\d+)', name_low)
            major_v = int(v_match.group(1)) if v_match else 0
            
            # Escludi modelli specializzati o non ancora accessibili
            # Consenti 'preview' solo per versioni >= 3 (come Gemini 3.1 Pro/Flash)
            tokens_to_exclude = ['exp', 'vision', 'latest', 'image', 'tts', 'computer', 'customtools']
            if major_v < 3:
                tokens_to_exclude.append('preview')
                
            if any(tok in name_low for tok in tokens_to_exclude):
                continue
            valid.append(name)

        if not valid:
            # Fallback hardcoded per tier
            fallbacks = {
                "pro": "gemini-2.5-pro",
                "flash": "gemini-2.5-flash",
                "best": "gemini-2.5-pro",
            }
            return fallbacks.get(preferred, "gemini-2.5-flash")

        # Ordina per capacità decrescente
        valid.sort(key=_model_capability_score, reverse=True)
        logging.debug(f"[AI-UTILS] Modelli disponibili (ordinati): {valid}")

        if preferred == "best":
            return valid[0]

        if preferred == "pro":
            # Pro ha precedenza; "preview" è accettato perché i pro sono in preview
            candidates = [v for v in valid if 'pro' in v.lower()]
            return candidates[0] if candidates else valid[0]

        if preferred == "flash":
            # Preferisci flash non-lite; accetta lite solo se non c'è altro flash
            non_lite = [v for v in valid if 'flash' in v.lower() and 'lite' not in v.lower()]
            if non_lite:
                return non_lite[0]
            lite = [v for v in valid if 'flash' in v.lower()]
            return lite[0] if lite else valid[0]

        # Fallback generico: miglior modello disponibile
        return valid[0]

    except Exception as e:
        logging.warning(f"[AI-UTILS] Impossibile scansionare modelli: {e}. Uso fallback.")
        if preferred == "pro":
            return "gemini-2.5-pro"
        return "gemini-2.5-flash"

def rotate_key_on_error(provider, current_key, km=None):
    """
    Tenta di ottenere la prossima chiave disponibile per un provider.
    Ritorna (nuova_chiave, ha_fatto_giro_completo).
    """
    if km is None:
        km = KeyManager()
    return km.get_next_key(provider, current_key)
