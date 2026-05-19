import requests, json, re

# crt.sh: tutti i certificati per *.findbuch.net
r = requests.get(
    'https://crt.sh/?q=%.findbuch.net&output=json',
    timeout=30,
    headers={'User-Agent': 'Mozilla/5.0', 'Accept': 'application/json'}
)
print('Status:', r.status_code, 'len:', len(r.text))
if not r.text.strip():
    print('Risposta vuota')
    exit()

data = r.json()
subs = set()
for entry in data:
    for name in entry.get('name_value', '').split('\n'):
        name = name.strip().lower()
        if name.endswith('.findbuch.net') and '*' not in name:
            sub = name.replace('.findbuch.net', '')
            subs.add(sub)

print(f'\nTotale subdomain: {len(subs)}')
print()
# Tenta di identificare italiani per keywords
italian_kw = ['ks', 'suedtirol', 'tirol', 'alto', 'bozen', 'bressanone',
              'trento', 'trent', 'kirchenbuch', 'kirchen', 'italia',
              'xn--', 'bozner', 'meran', 'bruneck', 'brixen']

print('=== Probabilmente ITALIANI ===')
for s in sorted(subs):
    if any(k in s for k in italian_kw):
        print(' ', s)

print()
print('=== TUTTI i subdomain ===')
for s in sorted(subs):
    print(' ', s)
