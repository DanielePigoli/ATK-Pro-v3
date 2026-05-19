import requests, re

url = 'https://data.matricula-online.eu/de/oesterreich/wien/01-st-stephan/01-001/'
r = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=15)
r.encoding = 'utf-8'
html = r.text

# Cerca data-* attributes (spesso usati per passare dati al viewer JS)
data_attrs = re.findall(r'data-[a-z\-]+=["\'"][^"\']{3,200}["\']', html)
print('Data attributes:')
for d in data_attrs[:30]:
    print(' ', d[:150])

print()
# Cerca variabili JS inizializzate
js_vars = re.findall(r'var\s+\w+\s*=\s*["\'{[][^;]{5,300}', html)
print('JS var inizializzate:')
for v in js_vars[:20]:
    print(' ', v[:200])

print()
# Cerca window. o document.
win_vars = re.findall(r'window\.\w+\s*=\s*[^;]{5,200}', html)
print('window.*:')
for v in win_vars[:10]:
    print(' ', v[:200])

print()
# Cerca endpoint API espliciti  
apis = re.findall(r'["\']/(api|iiif|imageapi|viewer|scan|image)[^"\']{0,100}["\']', html, re.IGNORECASE)
print('API endpoints:')
for a in sorted(set(apis))[:20]:
    print(' ', a)

print()
# Cerca id numerici (spesso l'id del registro è passato inline)
ids = re.findall(r'"(book_id|registry_id|matrikel_id|id|pk)"\s*:\s*(\d+)', html, re.IGNORECASE)
print('IDs numerici:')
for i in ids[:10]:
    print(' ', i)

# Dump sezione centrale dell'HTML (dove di solito ci sono i dati del viewer)
# Cerca il div principale del viewer
viewer_div = re.search(r'<div[^>]*imageview[^>]*>.*?</div>', html, re.DOTALL)
if viewer_div:
    print()
    print('Viewer div:')
    print(viewer_div.group()[:500])
