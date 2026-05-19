import requests, re

url = 'https://data.matricula-online.eu/de/oesterreich/wien/01-st-stephan/01-001/'
r = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=15)
r.encoding = 'utf-8'
html = r.text

# Salva tutto l'HTML per ispezione manuale
with open('_mat_page.html', 'w', encoding='utf-8') as f:
    f.write(html)
print('Salvato _mat_page.html')

# Stampa tutti gli script tags completi
scripts = re.findall(r'<script[^>]*>(.*?)</script>', html, re.DOTALL)
for i, s in enumerate(scripts):
    if s.strip():
        print(f'\n=== SCRIPT {i} (len={len(s)}) ===')
        print(s[:1000])
