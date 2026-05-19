import sys, re, requests
sys.path.insert(0, 'src')
from manifest_utils import build_matricula_synthetic_manifest

# Prima: controlla struttura pagina parrocchia RC
url_parish = 'https://data.matricula-online.eu/de/italien/IT-RC/IT-Ba_S-Teodoro/'
r = requests.get(url_parish, headers={'User-Agent': 'Mozilla/5.0'}, timeout=15)
r.encoding = 'utf-8'
print('Status:', r.status_code, 'Len:', len(r.text))

# Link a libri
books = re.findall(r'href=["\']([^"\']*IT-Ba_S-Teodoro/[^"\']+)["\']', r.text)
print('Link libri:', books[:10])

# Redirect esterno?
ext_links = re.findall(r'archiviodiocesano[^\s"\'<>]+', r.text)
print('Link esterni:', ext_links[:5])

# Cerca MatriculaDocView (viewer immagini)
has_viewer = 'MatriculaDocView' in r.text
print('Ha viewer:', has_viewer)

# Cerca tutti gli href nella pagina
all_href = re.findall(r'href=["\']([^"\']+)["\']', r.text)
rc_links = [h for h in all_href if 'IT-RC' in h or 'IT-Ba' in h]
print('Link RC:', rc_links[:10])
