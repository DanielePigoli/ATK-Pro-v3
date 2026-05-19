import requests

# be_id=23, ve_id=92 per Andrian (dal JS inline), count=0 = prima immagine
url = 'https://www.xn--kirchenbcher-sdtirol-wecg.findbuch.net/php/gtpc.php'
params = {'be_id': 23, 've_id': 92, 'count': 0}
h = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Referer': 'https://www.xn--kirchenbcher-sdtirol-wecg.findbuch.net/php/view.php?link=4b425f414e445249414e5f414e445249414e4fx10',
}
r = requests.get(url, headers=h, params=params, timeout=20)
print('Status:', r.status_code)
print('CT:', r.headers.get('content-type'))
print('Size:', len(r.content))
print('Primi 20 bytes:', r.content[:20])
if r.status_code == 200:
    with open('_gtpc_test_out.jpg', 'wb') as f:
        f.write(r.content)
    print('Salvato in _gtpc_test_out.jpg')
