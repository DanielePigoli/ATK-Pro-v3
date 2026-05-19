import requests, re

r = requests.get(
    'https://data.matricula-online.eu/de/italien/bozen-brixen/',
    headers={'User-Agent': 'Mozilla/5.0'},
    timeout=15
)
r.encoding = 'utf-8'

print('Status:', r.status_code)
print('Ha MatriculaDocView:', 'MatriculaDocView' in r.text)
ext = re.findall(r'findbuch[^\s"\'<>]+', r.text)
print('Link findbuch:', ext[:5])
all_hrefs = re.findall(r'href=["\']([^"\']+)["\']', r.text)
print('Tutti href:')
for h in all_hrefs:
    if 'bozen' in h or 'brixen' in h or 'kirchenbuch' in h or 'findbuch' in h:
        print(' ', h)
print()
clean = re.sub(r'<[^>]+>', ' ', r.text)
clean = re.sub(r'\s+', ' ', clean)
print('Testo:', clean[300:1500])
