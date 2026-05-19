import requests, re

# Scarica una pagina parrocchia Matricula SENZA redirect
# per vedere il vero HTML
r = requests.get(
    'https://data.matricula-online.eu/de/oesterreich/wien/01-st-stephan/',
    headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'},
    timeout=15,
    allow_redirects=True   # segue redirect
)
r.encoding = 'utf-8'
print(f'URL finale: {r.url}')
print(f'Status: {r.status_code}')
print(f'Len: {len(r.text)}')
print()

# Cerca pattern API/IIIF/immagini
for pattern in [r'iiif', r'manifest', r'api/', r'image/', r'cdn-', r'\.jpg', r'\.jpeg', r'\.tif']:
    matches = re.findall(r'[^\s"\'<>]{0,50}' + pattern + r'[^\s"\'<>]{0,80}', r.text, re.IGNORECASE)
    if matches:
        print(f'Pattern "{pattern}":')
        for m in sorted(set(matches))[:5]:
            print(f'  {m}')
        print()
