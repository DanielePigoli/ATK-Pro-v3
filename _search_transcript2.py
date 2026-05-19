import re
path = r'c:\Users\danie\AppData\Roaming\Code\User\workspaceStorage\54268263e3c45ae3be8b9c20bb73aa69\GitHub.copilot-chat\transcripts\576734da-0d92-45d6-ad12-68c755105b79.jsonl'
with open(path, encoding='utf-8') as f:
    content = f.read()
# Cerca contesto intorno a "3 TIFF" o "modalita D" o test funzionante
for pattern in ['3 TIFF', 'modalit', 'funzionante', 'scaricati', 'Registro con']:
    hits = [(m.start(), m.end()) for m in re.finditer(pattern, content, re.IGNORECASE)]
    for start, end in hits[:3]:
        snippet = content[max(0,start-100):end+200]
        print(f"=== {pattern} ===")
        print(snippet.replace('\n', ' ')[:400])
        print()
