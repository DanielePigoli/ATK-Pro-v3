import requests

# Cerca un registro Matricula con viewer + immagini
# Prova Slovenia che ha buona copertura
test_urls = [
    'https://data.matricula-online.eu/de/slovenia/',
    'https://data.matricula-online.eu/de/oesterreich/salzburg/',
    'https://data.matricula-online.eu/de/oesterreich/wien/',
]

for url in test_urls:
    r = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=10, allow_redirects=False)
    loc = r.headers.get('Location', '')
    print(f"Status {r.status_code} | {url[:70]} -> {loc[:80]}")
