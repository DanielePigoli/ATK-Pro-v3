import os
import csv
from PySide6.QtCore import QStandardPaths

SUPPORTED_AI_PROVIDERS = (
    "Gemini",
    "OpenAI",
    "Claude",
    "Mistral",
    "xAI",
    "DeepSeek",
    "Groq",
    "HuggingFace",
    "Ollama",
    "Transkribus",
)

PROVIDER_NOTES = {
    "Gemini": "Inserisci qui la tua chiave Gemini (Censimento/Genealogia)",
    "OpenAI": "Inserisci qui la tua chiave OpenAI",
    "Claude": "Inserisci qui la tua chiave Claude (Anthropic)",
    "Mistral": "Inserisci qui la tua chiave Mistral",
    "xAI": "Inserisci qui la tua chiave xAI / Grok",
    "DeepSeek": "Inserisci qui la tua chiave DeepSeek",
    "Groq": "Inserisci qui la tua chiave Groq",
    "HuggingFace": "Inserisci qui la tua chiave Hugging Face",
    "Ollama": "Inserisci qui l'host Ollama se diverso da http://localhost:11434",
    "Transkribus": "Inserisci email:password oppure Bearer token Transkribus",
}

PROVIDER_ALIASES = {
    "ANTHROPIC": "Claude",
    "CLAUDE": "Claude",
    "GEMINI": "Gemini",
    "GOOGLE": "Gemini",
    "OPENAI": "OpenAI",
    "GPT": "OpenAI",
    "MISTRAL": "Mistral",
    "GROQ": "Groq",
    "DEEPSEEK": "DeepSeek",
    "DEEP SEEK": "DeepSeek",
    "XAI": "xAI",
    "X.AI": "xAI",
    "GROK": "xAI",
    "HUGGINGFACE": "HuggingFace",
    "HUGGING FACE": "HuggingFace",
    "HF": "HuggingFace",
    "OLLAMA": "Ollama",
    "TRANSKRIBUS": "Transkribus",
}


def _empty_key_map():
    return {provider: [] for provider in SUPPORTED_AI_PROVIDERS}


def normalize_provider_name(provider):
    normalized = str(provider or "").strip()
    if not normalized:
        return ""
    compact = normalized.upper().replace("-", " ").replace("_", " ")
    compact_no_space = compact.replace(" ", "")
    for alias, canonical in PROVIDER_ALIASES.items():
        if alias in compact or alias in compact_no_space:
            return canonical
    for canonical in SUPPORTED_AI_PROVIDERS:
        if normalized.lower() == canonical.lower():
            return canonical
    return normalized


class KeyManager:
    def __init__(self, app_name="ATK-Pro", file_path=None):
        self.app_name = app_name
        self.file_path = file_path or self._get_keys_file_path()
        self.keys = _empty_key_map()
        self.current_indices = {}
        self.load_keys()

    def _get_keys_file_path(self):
        docs = QStandardPaths.writableLocation(QStandardPaths.StandardLocation.DocumentsLocation)
        base = os.path.join(docs, self.app_name)
        if not os.path.exists(base):
            try: os.makedirs(base, exist_ok=True)
            except: pass
        return os.path.join(base, "api_keys.csv")

    def load_keys(self):
        # Reset
        self.keys = _empty_key_map()
        if not os.path.exists(self.file_path):
            self._create_default_file()
            return

        try:
            existing_providers = set()
            with open(self.file_path, mode='r', encoding='utf-8-sig') as f:
                first_line = f.readline()
                if not first_line:
                    self._create_default_file()
                    return
                # Default delimiter
                delimiter = ';' 
                f.seek(0)
                if 'sep=' in first_line:
                    if 'sep=,' in first_line: delimiter = ','
                    f.readline() # skip sep line
                
                reader = csv.DictReader(f, delimiter=delimiter)
                for row in reader:
                    prov = row.get('Provider', '').strip()
                    key = row.get('Key', '').strip()
                    # Normalizzazione nomi provider per matchare l'interfaccia
                    prov = normalize_provider_name(prov)
                    if prov in self.keys:
                        existing_providers.add(prov)
                    if prov in self.keys and key:
                        self.keys[prov].append(key)
            self._append_missing_provider_rows(existing_providers, delimiter)
        except Exception as e:
            print(f"DEBUG: Errore caricamento chiavi: {e}")

    def _create_default_file(self):
        try:
            with open(self.file_path, mode='w', encoding='utf-8-sig', newline='') as f:
                f.write("sep=;\r\n")
                writer = csv.writer(f, delimiter=';')
                writer.writerow(['Provider', 'Key', 'Note'])
                for provider in SUPPORTED_AI_PROVIDERS:
                    writer.writerow([provider, '', PROVIDER_NOTES.get(provider, '')])
        except: pass

    def _append_missing_provider_rows(self, existing_providers, delimiter=';'):
        missing = [
            provider for provider in SUPPORTED_AI_PROVIDERS
            if provider not in existing_providers
        ]
        if not missing:
            return
        try:
            with open(self.file_path, mode='a', encoding='utf-8', newline='') as f:
                writer = csv.writer(f, delimiter=delimiter)
                for provider in missing:
                    writer.writerow([provider, '', PROVIDER_NOTES.get(provider, '')])
        except Exception as e:
            print(f"DEBUG: Errore aggiornamento righe provider chiavi: {e}")

    def get_all_keys(self, provider):
        return self.keys.get(normalize_provider_name(provider), [])

    def get_next_key(self, provider, current_key=None):
        """Ritorna (chiave, ha_fatto_il_giro_completo)."""
        provider = normalize_provider_name(provider)
        keys = self.get_all_keys(provider)
        if not keys: return None, False
        
        if current_key not in keys:
            self.current_indices[provider] = 0
            return keys[0], False
        
        if len(keys) == 1:
            return keys[0], True
            
        idx = keys.index(current_key)
        next_idx = (idx + 1) % len(keys)
        
        # Se siamo tornati alla prima (index 0), abbiamo completato il giro
        wrapped = (next_idx == 0)
        
        self.current_indices[provider] = next_idx
        return keys[next_idx], wrapped

    def has_multiple_keys(self, provider):
        return len(self.get_all_keys(normalize_provider_name(provider))) > 1

    def has_keys(self, provider):
        """Ritorna True se il provider ha almeno una chiave configurata."""
        return len(self.get_all_keys(normalize_provider_name(provider))) > 0
