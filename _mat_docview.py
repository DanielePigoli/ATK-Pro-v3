import requests, re, json

url = 'https://data.matricula-online.eu/de/oesterreich/wien/01-st-stephan/01-001/'
r = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=15)
r.encoding = 'utf-8'
html = r.text

# Trova la chiamata MatriculaDocView con i dati
m = re.search(r'new arc\.imageview\.MatriculaDocView\("document",\s*(\{.*?\})\s*\);', html, re.DOTALL)
if not m:
    print('MatriculaDocView non trovato')
    # Proviamo a trovare la stringa
    idx = html.find('MatriculaDocView')
    if idx >= 0:
        print('Trovato a', idx)
        print(html[idx:idx+2000])
else:
    data_str = m.group(1)
    print('Dati trovati, len:', len(data_str))
    print()
    print('Primi 2000 char:')
    print(data_str[:2000])
    print()
    print('Ultimi 500 char:')
    print(data_str[-500:])
