# ai_search_prompts.py
# Prompt AI localizzati tramite glossario multilingue ATK-Pro

import os
import sys

def get_msg(glossario, chiave, lingua):
    lingua = lingua.upper()
    # Cerca in tutte le sezioni del glossario
    for section in glossario.values():
        if isinstance(section, list):
            for voce in section:
                if voce.get("messaggio") == chiave:
                    return voce.get(lingua, voce.get("IT", None))
    return None

def get_prompt_base(glossario, lingua="it", idx=0, **kwargs):
    """
    Recupera il prompt AI localizzato dal glossario multilingue.
    Le chiavi devono essere:
      - "AI_PROMPT_1"
      - "AI_PROMPT_2"
      - "AI_PROMPT_3"
      - "AI_PROMPT_4"
    """
    chiave = f"AI_PROMPT_{idx+1}"
    prompt = get_msg(glossario, chiave, lingua)
    if not prompt:
        # Fallback: italiano
        prompt = get_msg(glossario, chiave, "IT")
    if not prompt:
        raise ValueError(f"Prompt non trovato nel glossario: {chiave} [{lingua}]")
    return prompt.format(**kwargs)
