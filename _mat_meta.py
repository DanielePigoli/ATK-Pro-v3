import requests, re, base64

url = 'https://data.matricula-online.eu/de/oesterreich/wien/01-st-stephan/01-001/'
r = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=15)
r.encoding = 'utf-8'
html = r.text

# Cerca titolo del registro (nome del libro)
title_patterns = [
    r'<title>([^<]+)</title>',
    r'<h1[^>]*>([^<]+)</h1>',
    r'<h2[^>]*>([^<]+)</h2>',
    r'"title":\s*"([^"]+)"',
    r'"name":\s*"([^"]+)"',
    r'register_name[^"]*"([^"]+)"',
]
for pat in title_patterns:
    m = re.search(pat, html, re.IGNORECASE)
    if m:
        print(f'Titolo ({pat[:30]}): {m.group(1)[:100]}')

# Cerca metadati del registro (anno, tipo, ecc.)
meta_patterns = [
    r'"date_from":\s*"([^"]+)"',
    r'"date_to":\s*"([^"]+)"',
    r'"type":\s*"([^"]+)"',
    r'"signature":\s*"([^"]+)"',
]
for pat in meta_patterns:
    m = re.search(pat, html, re.IGNORECASE)
    if m:
        print(f'Meta: {m.group(0)[:100]}')

# Testa accesso immagine con/senza referer
img_url = 'http://hosted-images.matricula-online.eu/images/matricula/NAS_Matricula_Online/9001M/01-01/Wiensanktstephan_01-01_1585_1589_9001_01-Einband_0001.jpg'
r2 = requests.get(img_url, headers={'User-Agent': 'Mozilla/5.0', 'Referer': 'https://data.matricula-online.eu/'}, timeout=15)
print(f'\nImg con Referer: {r2.status_code} {len(r2.content)} bytes')
r3 = requests.get(img_url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=15)
print(f'Img senza Referer: {r3.status_code} {len(r3.content)} bytes')
