import json, pathlib, re, sys

GLOSSARY_PATH = pathlib.Path(r'c:/ATK-Pro_v3.0/docs_generali/glossario_multilingua_ATK-Pro.json')

SUPPORTED_LANGUAGES = [
    "IT", "EN", "ES", "FR", "DE", "PT", "RU", "AR", "NL", "HE", "JA", "SV", "ZH", "RO", "EL", "PL", "DA", "NO", "TR", "VI"
]
TECHNICAL_TERMS = {"PDF", "HTML", "OCR", "CUI", "ATK_Pro", "Antenati ToolKit Pro"}

try:
    raw_text = GLOSSARY_PATH.read_text(encoding='utf-8')
    # Locate the first opening brace to skip any preamble
    first_brace = raw_text.find('{')
    if first_brace != -1:
        raw_text = raw_text[first_brace:]
    # Normalize line endings to LF for json5 parsing
    raw_text = raw_text.replace('\r\n', '\n')
    data = json.loads(raw_text)
except Exception as e:
    print('ERROR loading JSON with json5:', e)
    sys.exit(1)

issues = []
for section, entries in data.items():
    if not isinstance(entries, list):
        continue
    for idx, entry in enumerate(entries):
        if not isinstance(entry, dict):
            issues.append(f"Entry {section}[{idx}] is not a dict")
            continue
        # Check that all supported languages exist
        for lang in SUPPORTED_LANGUAGES:
            if lang not in entry:
                issues.append(f"Missing language {lang} in {section}[{idx}]")
        # Ensure invariant technical terms present in IT are kept unchanged in other languages.
        it_text = entry.get('IT', '')
        tokens = re.findall(r'\b[A-Z]{2,}\b', it_text)
        for token in tokens:
            if token not in TECHNICAL_TERMS:
                continue
            for lang in SUPPORTED_LANGUAGES:
                if token not in entry.get(lang, ''):
                    issues.append(f"Technical term {token} missing in {lang} for {section}[{idx}]")

if not issues:
    print('JSON glossary is valid and consistent.')
else:
    print('Found issues:')
    for i in issues:
        print(i)
