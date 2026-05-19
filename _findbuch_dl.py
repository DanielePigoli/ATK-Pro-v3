import requests, re

r = requests.get(
    'https://www.findbuch.net/hp/Institutionen/',
    headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'},
    timeout=20
)
r.encoding = 'utf-8'
with open('_inst.html', 'w', encoding='utf-8') as f:
    f.write(r.text)
print('OK len', len(r.text))
