#!/usr/bin/env python3
import json, pathlib, re, sys

GLOSSARY_PATH = pathlib.Path(r'c:/ATK-Pro_v3.0/docs_generali/glossario_multilingua_ATK-Pro.json')

SUPPORTED_LANGUAGES = [
    "IT", "EN", "ES", "FR", "DE", "PT", "RU", "AR", "HE", "JA", "SV", "ZH", "RO", "EL", "PL", "DA", "NO", "TR", "VI"
]

TECHNICAL_TERMS = {"PDF", "HTML", "CUI", "ATK_Pro", "Antenati ToolKit Pro"}

def load_json(path: pathlib.Path):
    raw = path.read_text(encoding='utf-8')
    # Remove any leading characters before the first '{'
    first_brace = raw.find('{')
    if first_brace != -1:
        raw = raw[first_brace:]
    try:
        return json.loads(raw)
    except Exception as e:
        print('ERROR loading JSON:', e, file=sys.stderr)
        sys.exit(1)

glossary = load_json(GLOSSARY_PATH)
issues = []
for section, entries in glossary.items():
    if not isinstance(entries, list):
        continue
    for idx, entry in enumerate(entries):
        if not isinstance(entry, dict):
            issues.append(f"Entry {section}[{idx}] is not a dict")
            continue
        # Ensure all languages present
        for lang in SUPPORTED_LANGUAGES:
            if lang not in entry:
                issues.append(f"Missing language {lang} in {section}[{idx}]")
        # Check technical terms from IT text
        it_text = entry.get('IT', '')
        tokens = re.findall(r'\b[A-Z]{2,}\b', it_text)
        for token in tokens:
            if token in TECHNICAL_TERMS:
                for lang in SUPPORTED_LANGUAGES:
                    if token not in entry.get(lang, ''):
                        issues.append(f"Technical term {token} missing in {lang} for {section}[{idx}]")

if issues:
    print('Found issues:')
    for i in issues:
        print(i)
    sys.exit(1)
else:
    print('JSON glossary is valid and consistent.')
