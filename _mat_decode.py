import requests, re, json, base64

url = 'https://data.matricula-online.eu/de/oesterreich/wien/01-st-stephan/01-001/'
r = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=15)
r.encoding = 'utf-8'
html = r.text

# Estrai i dati del viewer (con regex greedy per catturare tutto il JSON)
# La struttura ha un array "images" con URL base64
img_urls = re.findall(r'"/image/([A-Za-z0-9+/=]+)"', html)
print(f'URL immagini trovati: {len(img_urls)}')
print()

# Decodifica i primi 5
for encoded in img_urls[:5]:
    try:
        decoded = base64.b64decode(encoded + '==').decode('utf-8')
        print(f'Encoded: {encoded[:40]}...')
        print(f'Decoded: {decoded}')
        print()
    except Exception as e:
        print(f'Errore decodifica: {e}')

# Estrai anche "path"
path_m = re.search(r'"path":\s*"([^"]+)"', html)
if path_m:
    print(f'Base path: {path_m.group(1)}')

# Estrai labels
labels_m = re.search(r'"labels":\s*\[([^\]]+)\]', html)
if labels_m:
    labels = re.findall(r'"([^"]+)"', labels_m.group(1))
    print(f'\nTotale pagine (labels): {len(labels)}')
    print(f'Prime 5: {labels[:5]}')
    print(f'Ultime 5: {labels[-5:]}')
