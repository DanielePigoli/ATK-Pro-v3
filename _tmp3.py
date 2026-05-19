import requests
test_guid = '00000000-0000-0000-0000-000000000001'
for sub in ['parma','modena','bologna','bergamo','verona','padova','venezia','firenze']:
    url = f'https://{sub}.jarvis.memooria.org/meta/iiif/{test_guid}/manifest'
    r = requests.get(url, timeout=5, headers={'User-Agent':'Mozilla/5.0'})
    ct = r.headers.get('Content-Type','')[:25]
    print(f'{r.status_code} {sub:12s} [{ct}]')
