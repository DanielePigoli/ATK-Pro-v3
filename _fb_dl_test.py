import requests

url = 'https://www.findbuch.net/a_pics/ks/W.._13_3._~ARCHIVALIEN_A._~AA6._~KIRCHENBUECHER._~KB_ABTEI_BADIA._~121_08._~121_08_003.jpg'
referers = [
    'https://www.xn--kirchenbcher-sdtirol-wecg.findbuch.net/',
    'https://www.xn--kirchenbcher-sdtirol-wecg.findbuch.net/php/view.php?link=4b425f41425445495f4241444941x1',
    'https://www.findbuch.net/',
    None,
]
ua = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124.0.0.0 Safari/537.36'

for ref in referers:
    h = {'User-Agent': ua}
    if ref:
        h['Referer'] = ref
    try:
        r = requests.get(url, headers=h, timeout=15)
        ct = r.headers.get('content-type', '?')
        print(f"Referer={str(ref)[:60]!r} -> {r.status_code}, {len(r.content)} bytes, {ct}")
    except Exception as e:
        print(f"Referer={str(ref)[:60]!r} -> ERRORE: {e}")
