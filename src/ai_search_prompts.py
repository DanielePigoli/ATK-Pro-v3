# ai_search_prompts.py
# Prompt di base per la ricerca genealogica assistita AI in ATK-Pro

PROMPT_BASE = {
    "it": [
        # Prompt 1: Ricerca generale dettagliata
        "Suggerisci i portali e aggregatori digitali più adatti per una ricerca genealogica su: {query}. Per ciascun portale, indica:\n- Una breve motivazione\n- Una query di esempio\n- Il periodo coperto\n- Il tipo di atti disponibili\nRispondi in tabella con colonne: Portale, Motivazione, Query di esempio, Periodo, Tipo atti.",
        # Prompt 2: Strategie internazionali dettagliate
        "Quali strategie di ricerca genealogica internazionale consiglieresti per: {query}? Elenca anche portali e archivi utili relativi a {luogo} nel periodo {periodo} per atti di tipo {tipo}. Per ciascun portale, aggiungi motivazione e query di esempio. Rispondi in tabella con colonne: Strategia/Portale, Motivazione, Query di esempio, Periodo, Tipo atti.",
        # Prompt 3: Ricerca atti specifici dettagliata
        "Genera una lista di portali digitali e archivi utili per la ricerca di atti {tipo} relativi a {luogo} nel periodo {periodo}. Per ciascun portale, indica motivazione, query di esempio e periodo coperto. Rispondi in tabella con colonne: Portale, Motivazione, Query di esempio, Periodo, Tipo atti.",
        # Prompt 4: Ricerca avanzata con filtri
        "Per la ricerca di {query} (luogo: {luogo}, periodo: {periodo}, tipo: {tipo}), quali portali digitali e aggregatori sono più indicati? Suggerisci anche eventuali filtri avanzati o strategie alternative. Per ciascun portale, aggiungi motivazione e query di esempio. Rispondi in tabella con colonne: Portale, Motivazione, Query di esempio, Periodo, Tipo atti, Filtri/Strategie.",
    ],
    "en": [
        # Prompt 1: General detailed search
        "Suggest the best digital portals and aggregators for genealogical research on: {query}. For each portal, provide:\n- A short reason\n- A sample query\n- The period covered\n- The type of records available\nReply in a table with columns: Portal, Reason, Sample Query, Period, Record Type.",
        # Prompt 2: International strategies detailed
        "What international genealogy research strategies would you recommend for: {query}? Also list useful portals and archives related to {place} in the period {period} for {type} records. For each portal, add a reason and a sample query. Reply in a table with columns: Strategy/Portal, Reason, Sample Query, Period, Record Type.",
        # Prompt 3: Specific record search detailed
        "Generate a list of digital portals and archives useful for searching {type} records related to {place} in the period {period}. For each portal, provide a reason, a sample query, and the period covered. Reply in a table with columns: Portal, Reason, Sample Query, Period, Record Type.",
        # Prompt 4: Advanced search with filters
        "For the research on {query} (place: {place}, period: {period}, type: {type}), which digital portals and aggregators are most suitable? Also suggest advanced filters or alternative strategies. For each portal, add a reason and a sample query. Reply in a table with columns: Portal, Reason, Sample Query, Period, Record Type, Filters/Strategies.",
    ]
}

# Funzioni di utilità per recupero prompt base

def get_prompt_base(lang="it", idx=0, **kwargs):
    prompts = PROMPT_BASE.get(lang, PROMPT_BASE["it"])
    prompt = prompts[idx % len(prompts)]
    return prompt.format(**kwargs)
