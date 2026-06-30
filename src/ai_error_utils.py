from key_manager import normalize_provider_name


def classify_ai_runtime_error(provider, raw_error):
    provider_name = normalize_provider_name(provider) or str(provider or "provider AI")
    message = str(raw_error or "").strip()
    lower = message.lower()

    if not message:
        return f"Errore AI non specificato per {provider_name}."

    if any(token in lower for token in ["api_key", "unauthorized", "invalid api key", "invalid_api_key", "authentication", "forbidden", "permission denied"]):
        return f"Credenziali non valide o non abilitate per {provider_name}. Verifica chiave, permessi e fatturazione."

    if any(token in lower for token in ["429", "quota", "resource_exhausted", "rate limit", "too many requests", "limit: 0"]):
        return f"Quota o limite richieste esaurito per {provider_name}. Attendi e riprova, oppure usa un'altra chiave/provider."

    if any(token in lower for token in ["model", "modello"]) and any(token in lower for token in ["404", "not found", "does_not_exist", "unknown", "unsupported"]):
        return f"Modello AI non disponibile per {provider_name}. Verifica l'override modello oppure riprova con quello predefinito."

    if any(token in lower for token in ["risposta", "response", "content", "json"]) and any(token in lower for token in ["non valida", "vuota", "empty", "invalid", "malformed", "missing"]):
        return f"Il provider {provider_name} ha restituito una risposta non valida o vuota. Riprova tra poco."

    if "tutte le chiavi" in lower or "all keys" in lower:
        return f"Tutte le chiavi disponibili per {provider_name} risultano non utilizzabili al momento. Controlla quota, validita' credenziali o provider alternativo."

    return f"Errore AI con {provider_name}: {message}"
