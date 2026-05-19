import sys
import requests

sys.path.append('src')
from manifest_utils import build_internetculturale_estense_synthetic_manifest

# Smoke rapido su 2 OAI reali Estense (tempo contenuto).
URLS = [
    "https://www.internetculturale.it/it/16/search/viewresource?id=oai%3Awww.internetculturale.sbn.it%2FTeca%3A20%3ANT0000%3AMO0089_A.M-18.6&case=&instanceName=mag&descSource=Biblioteca+digitale&descSourceLevel2=MagTeca+-+ICCU",
    "https://www.internetculturale.it/it/16/search/viewresource?id=oai%3Awww.internetculturale.sbn.it%2FTeca%3A20%3ANT0000%3AMO0089_A.M-18.4.b&case=&instanceName=mag&descSource=Biblioteca+digitale&descSourceLevel2=MagTeca+-+ICCU",
]


def validate(url: str) -> bool:
    m = build_internetculturale_estense_synthetic_manifest(url)
    if not isinstance(m, dict):
        print("manifest: FAIL")
        return False

    canv = m.get('sequences', [{}])[0].get('canvases', [])
    if not canv:
        print("canvases: FAIL (0)")
        return False

    img = canv[0].get('images', [{}])[0].get('resource', {}).get('@id')
    svc = canv[0].get('images', [{}])[0].get('resource', {}).get('service', {})
    if svc.get('@context') != 'internetculturale_cacheman_direct':
        print("service: FAIL")
        return False

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    # stream=True: verifica status/header senza scaricare tutto il payload.
    with requests.get(img, headers=headers, timeout=(8, 20), stream=True) as r:
        ctype = r.headers.get('content-type', '')
        ok = r.ok and ('image' in ctype.lower())
        print(f"canvases={len(canv)} first_img_http={r.status_code} {ctype}")
        return ok


def main() -> int:
    print("=== Quick smoke InternetCulturale Estense (2 OAI) ===")
    passed = 0
    for i, u in enumerate(URLS, start=1):
        print(f"[{i}] {u}")
        if validate(u):
            passed += 1
        else:
            print("  -> FAIL")
    print(f"Risultato: {passed}/{len(URLS)}")
    return 0 if passed == len(URLS) else 1


if __name__ == '__main__':
    raise SystemExit(main())
