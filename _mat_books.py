import requests, re

# Scarica la pagina parrocchia Matricula completa per cercare gli URL dei libri
r = requests.get(
    'https://data.matricula-online.eu/de/oesterreich/wien/01-st-stephan/',
    headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'},
    timeout=15
)
r.encoding = 'utf-8'

html = r.text

# Cerca link a singoli libri (di solito href con un id numerico alla fine)
book_links = re.findall(r'href=["\']([^"\']*oesterreich/wien/01-st-stephan/[^"\']+)["\']', html)
print('Link libri trovati:')
for l in sorted(set(book_links))[:20]:
    print(' ', l)

print()
# Cerca struttura dati JS (spesso i libri sono in un array JSON inline)
json_data = re.findall(r'(registries|books|matrikel|buchtyp|taufbuch)[^\n]{0,200}', html, re.IGNORECASE)
print('Data JS:')
for j in json_data[:5]:
    print(' ', j[:200])

print()
# Cerca tutti gli href della pagina  
all_links = re.findall(r'href=["\']([^"\']+)["\']', html)
matrikel = [l for l in all_links if 'st-stephan' in l.lower() or 'stephan/' in l.lower()]
print('All links con st-stephan:')
for l in sorted(set(matrikel)):
    print(' ', l)
