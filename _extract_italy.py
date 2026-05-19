import re
from html.parser import HTMLParser

html = open('_inst.html', encoding='utf-8').read()

# Trova il blocco completo della sezione "Italien"
idx = html.find('"Italien"')
if idx < 0:
    idx = html.find('>Italien<')

print(f'Trovato a indice: {idx}')
print()
# Stampa un ampio contesto
block = html[idx:idx+3000]
print(block)

print()
print('=== TESTO PULITO ===')
# Rimuovi tag HTML
clean = re.sub(r'<[^>]+>', ' ', block)
clean = re.sub(r'\s+', ' ', clean)
print(clean)
