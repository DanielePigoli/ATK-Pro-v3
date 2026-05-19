import requests, re, json

# Analizza la pagina di un singolo libro/registro Matricula
url = 'https://data.matricula-online.eu/de/oesterreich/wien/01-st-stephan/01-001/'
r = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=15)
r.encoding = 'utf-8'
html = r.text

print(f'URL: {r.url}')
print(f'Status: {r.status_code}  Len: {len(html)}')
print()

# Cerca URL immagini
for pat in [r'cdn[^\s"\'<>]{5,120}', r'https?://[^\s"\'<>]*\.(jpg|jpeg|tif|png)[^\s"\'<>]*']:
    matches = re.findall(pat, html, re.IGNORECASE)
    if matches:
        print(f'Pattern immagini:')
        for m in sorted(set(matches))[:10]:
            print(f'  {m[:120]}')
        print()

# Cerca manifest IIIF
iiif = re.findall(r'[^\s"\'<>]*iiif[^\s"\'<>]*', html, re.IGNORECASE)
if iiif:
    print('IIIF refs:')
    for i in sorted(set(iiif))[:10]:
        print(f'  {i}')
    print()

# Cerca JSON inline (dati registro)
json_blocks = re.findall(r'\{[^{}]{20,500}\}', html)
print(f'JSON blocks trovati: {len(json_blocks)}')
# Cerca quelli con "image" o "page" 
for j in json_blocks:
    if any(k in j.lower() for k in ['image', 'page', 'folio', 'scan', 'file']):
        print(j[:300])
        print()

# Cerca <script> con dati
scripts = re.findall(r'<script[^>]*>(.*?)</script>', html, re.DOTALL)
print(f'\nScript tags: {len(scripts)}')
for s in scripts:
    if any(k in s.lower() for k in ['image', 'page', 'scan', 'folio', 'cdn']):
        print(s[:500])
        print('---')
