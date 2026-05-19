import re, sys
sys.stdout.reconfigure(encoding='utf-8')
path = r'c:\Users\danie\AppData\Roaming\Code\User\workspaceStorage\54268263e3c45ae3be8b9c20bb73aa69\GitHub.copilot-chat\transcripts\576734da-0d92-45d6-ad12-68c755105b79.jsonl'
with open(path, encoding='utf-8') as f:
    content = f.read()

for pattern in ['blockedVisible.*false', 'false.*blocked', 'immagine.*visibil', 'modalit.*D.*findbuch', 'findbuch.*funzion', 'findbuch.*TIFF', 'view.php.*link=', 'Abtei', 'link=4b42']:
    hits = [(m.start(), m.end()) for m in re.finditer(pattern, content, re.IGNORECASE)]
    for start, end in hits[:3]:
        snippet = content[max(0,start-80):end+200]
        print(f"=== {pattern} ===")
        print(snippet[:400])
        print()
