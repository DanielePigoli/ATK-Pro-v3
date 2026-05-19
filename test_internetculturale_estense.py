import re
import sys
import requests
from urllib.parse import quote_plus

BASE = "https://www.internetculturale.it"
DEFAULT_TECA = "MagTeca - ICCU"

# 5 OAI sample emersi dalla ricerca Estense su Internet Culturale.
SAMPLE_OAI_IDS = [
    "oai:www.internetculturale.sbn.it/Teca:20:NT0000:MO0089_A.M-18.6",
    "oai:www.internetculturale.sbn.it/Teca:20:NT0000:MO0089_A.M-40.2",
    "oai:www.internetculturale.sbn.it/Teca:20:NT0000:MO0089_A.M-18.4.a",
    "oai:www.internetculturale.sbn.it/Teca:20:NT0000:MO0089_A.M-18.4.b",
    "oai:www.internetculturale.sbn.it/Teca:20:NT0000:MO008916360",
]

UA = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}


def _extract_first_image_url(mag_text: str) -> str | None:
    # Evita i placeholder (book.jpg) e cerca direttamente le immagini pagina.
    m = re.search(r'src="(cacheman/normal/[^"]+\.(?:jpg|jpeg|png|jp2))"', mag_text, re.IGNORECASE)
    if not m:
        return None
    return f"{BASE}/jmms/{m.group(1)}"


def _count_pages(mag_text: str) -> int:
    return len(re.findall(r"<page\b", mag_text, flags=re.IGNORECASE))


def _fetch_mag(oai_id: str, teca: str = DEFAULT_TECA) -> tuple[str | None, str | None, str | None]:
    enc_oai = quote_plus(oai_id)
    enc_teca = quote_plus(teca)
    candidates = [
        f"{BASE}/jmms/magparser?id={enc_oai}&teca={enc_teca}&mode=all&fulltext=0",
        f"{BASE}/jmms/magparser?id={enc_oai}&mode=all&fulltext=0",
    ]

    for u in candidates:
        try:
            r = requests.get(u, headers=UA, timeout=35)
            if not r.ok:
                continue
            txt = r.text
            if "<page" in txt or "cacheman/normal/" in txt:
                return txt, u, None
        except Exception as e:
            err = str(e)
    return None, None, err if 'err' in locals() else "Nessuna risposta utile"


def main() -> int:
    print("=== Harness Internet Culturale / Estense (5 OAI) ===")
    ok = 0

    for i, oai in enumerate(SAMPLE_OAI_IDS, start=1):
        print(f"\n[{i}] OAI: {oai}")
        mag, mag_url, err = _fetch_mag(oai)
        if not mag:
            print(f"  MAG: FAIL ({err})")
            continue

        pages = _count_pages(mag)
        first_img = _extract_first_image_url(mag)
        print(f"  MAG: OK ({mag_url})")
        print(f"  Pagine rilevate: {pages}")

        if not first_img:
            print("  Prima immagine: FAIL (src cacheman non trovato)")
            continue

        try:
            ri = requests.get(first_img, headers=UA, timeout=35)
            ctype = ri.headers.get("content-type", "")
            print(f"  Prima immagine: HTTP {ri.status_code} {ctype}")
            if ri.ok and "image" in ctype.lower():
                ok += 1
        except Exception as e:
            print(f"  Prima immagine: FAIL ({e})")

    print(f"\nRisultato: {ok}/{len(SAMPLE_OAI_IDS)} OAI validati")
    return 0 if ok >= 3 else 1


if __name__ == "__main__":
    raise SystemExit(main())
