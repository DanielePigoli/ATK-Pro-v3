# -*- coding: utf-8 -*-
import requests, warnings, json, re
warnings.filterwarnings('ignore')
h = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/json,*/*',
}

item_id = 'birdbookillustra00reedrich'
server = 'ia800601.us.archive.org'
dir_ = '/33/items/' + item_id

# 1. Cerca manifest/BookReader URL nel sorgente HTML della pagina
r = requests.get('https://archive.org/details/' + item_id, headers=h, timeout=12)
text = r.text
iiif_matches = re.findall(r'https?://[^\s"\']+manifest[^\s"\']*', text)
br_matches   = re.findall(r'BookReaderJSON[^\s"\']+', text)
print('IIIF in HTML:', iiif_matches[:3])
print('BookReader in HTML:', br_matches[:2])

# 2. BookReaderImages - endpoint classico per servire pagine JP2
page0_file = item_id + '_jp2/' + item_id + '_0001.jp2'
zip_path   = dir_ + '/' + item_id + '_jp2.zip'
img_url = (
    'https://' + server +
    '/BookReader/BookReaderImages.php?zip=' + zip_path +
    '&file=' + page0_file +
    '&id=' + item_id +
    '&scale=1&rotate=0'
)
r2 = requests.get(img_url, headers=h, timeout=15)
ct2 = r2.headers.get('content-type', '')
print('\nBookReaderImages:', r2.status_code, ct2, 'size:', len(r2.content))

# 3. Prova anche il Scribe scandata XML per lista pagine
scandata_url = 'https://' + server + dir_ + '/' + item_id + '_scandata.xml'
r3 = requests.get(scandata_url, headers=h, timeout=10)
print('Scandata:', r3.status_code, r3.headers.get('content-type','')[:30])
if r3.ok:
    pages = re.findall(r'<page[^>]*>', r3.text)
    print('  pages found:', len(pages))
