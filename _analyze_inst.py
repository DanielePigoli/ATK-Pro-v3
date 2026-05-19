import re

html = open('_inst.html', encoding='utf-8').read()

# Cerca tutti gli URL findbuch
urls = re.findall(r'findbuch\.net', html)
print(f'Occorrenze "findbuch.net": {len(urls)}')

# Cerca href con findbuch
hrefs = re.findall(r'href=["\']([^"\']*findbuch[^"\']*)["\']', html)
print(f'\nHref con findbuch: {len(hrefs)}')
for h in hrefs:
    print(' ', h)

# Cerca sezione "Italien"
idx = html.find('Italien')
while idx >= 0:
    print(f'\n=== "Italien" @{idx} ===')
    print(html[max(0, idx-200):idx+500])
    idx = html.find('Italien', idx + 1)

# Cerca dati JSON map markers (LeafletJS o simili)
map_data = re.findall(r'L\.marker\([^)]+\).*?popup\([^)]+\)', html, re.DOTALL)
print(f'\nLeaflet markers: {len(map_data)}')
for m in map_data[:5]:
    print(m[:200])

# Cerca anche onclick con URL
onclicks = re.findall(r'onclick=["\'][^"\']*findbuch[^"\']*["\']', html)
print(f'\nonclick con findbuch: {len(onclicks)}')
for o in onclicks:
    print(' ', o)
