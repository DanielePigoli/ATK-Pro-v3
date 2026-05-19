# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
import re, requests

H = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}

# ---------------------------------------------------------------
# Europeana IIIF - cerca portali italiani con materiale genealogico
# Europeana aggrega e documenta quali provider offrono IIIF
# ---------------------------------------------------------------
print("=== Europeana - provider italiani IIIF con manoscritti/archivi ===")
europeana_url = 'https://api.europeana.eu/record/v2/search.json?wskey=api2demo&query=DATA_PROVIDER%3A%22*italia*%22+AND+TYPE%3ATEXT&reusability=open&media=true&qf=MIME_TYPE%3Aapplication%2Fjson&rows=10'
try:
    r = requests.get(europeana_url, headers=H, timeout=20)
    if r.status_code == 200:
        d = r.json()
        items = d.get('items', [])
        for item in items[:5]:
            print(f"  - {item.get('dataProvider',['?'])} | {item.get('title',['?'])[0][:50] if item.get('title') else '?'}")
    else:
        print(f"  HTTP {r.status_code}")
except Exception as e:
    print(f"  ERR: {e}")

# ---------------------------------------------------------------
# Cerca portali IIIF italiani con genealogia su Biblissima
# (aggregatore IIIF europeo, documenta provider italiani)
# ---------------------------------------------------------------
print("\n=== Biblissima IIIF - provider italiani ===")
biblissima_tests = [
    'https://portail.biblissima.fr/fr/iiif-collections',
    'https://api.biblissima.fr/repositories',
]
for u in biblissima_tests:
    try:
        r = requests.get(u, headers=H, timeout=15)
        txt = r.text
        # cerca provider italiani
        italian = re.findall(r'[^<>"]{0,30}(?:italia|firenze|venezia|napoli|roma|milano|torino|palermo|bologna|genova|sicilia|sardegna|calabria|puglia|campania|veneto|piemonte)[^<>"]{0,50}', txt, re.I)
        print(f"  {u.split('/')[-1]}: HTTP {r.status_code} | italian_refs={len(italian)}")
        for ref in list(set(italian))[:8]:
            print(f"    {ref.strip()[:80]}")
    except Exception as e:
        print(f"  ERR {u}: {type(e).__name__}")

# ---------------------------------------------------------------
# Test IIIF diretto: BNCF con identifier corretto (dai dati Biblissima)
# ---------------------------------------------------------------
print("\n=== BNCF Teca - identifier reali IIIF ===")
# L'ID BNCF usa formato differente - prova con endpoint più recente
bncf_tests = [
    'https://teca.bncf.firenze.sbn.it/teca/viewer/bncf:0001',
    'https://teca.bncf.firenze.sbn.it/iiif/manuscript/bncf.ms.b.16/manifest.json',
    'https://bncf.iiifhosting.com/iiif/manifest/bncf/2/manifest.json',
]
for u in bncf_tests:
    try:
        r = requests.get(u, headers=H, timeout=10)
        is_iiif = any(k in r.text[:300] for k in ['sequences', 'items', '@context'])
        print(f"  {r.status_code} | IIIF={is_iiif} | {u.split('/')[-1]}")
    except Exception as e:
        print(f"  ERR {u.split('/')[-1]}: {type(e).__name__}")

# ---------------------------------------------------------------
# Portali con IIIF documentato e materiale genealogico italiano
# che non abbiamo ancora verificato
# ---------------------------------------------------------------
print("\n=== Altri portali IIIF italiani non ancora in ATK-Pro ===")
altri = [
    # (nome, manifest_url_esempio)
    ('Archivio Segreto Vaticano (DigiVatLib)', 'https://digi.vatlib.it/iiif/MSS_Vat.lat.3225/manifest.json'),
    ('Europeana - Stato Civile aggregato', 'https://iiif.europeana.eu/presentation/9200356/BibliographicResource_3000100312200/manifest'),
    ('Digital Vatican Library', 'https://digi.vatlib.it/iiif/MSS_Reg.lat.12/manifest.json'),
    ('Archivio Apostolico Vaticano', 'https://digi.vatlib.it/iiif/MSS_Vat.ebr.1/manifest.json'),
    ('Cantaloupe IIIF Unibo', 'https://iiif.unibo.it/iiif/2/libro_ore_gonzaga/manifest.json'),
    ('Padova Univ - manoscritti', 'https://iiif.cab.unipd.it/iiif/2/ms1/manifest.json'),
    ('Torino BN - digitalizzazioni', 'https://www.bnto.librari.beniculturali.it/iiif/manifest/bnto.ms.b.0001/manifest.json'),
]
for nome, manifest_url in altri:
    try:
        r = requests.get(manifest_url, headers=H, timeout=15)
        is_iiif = any(k in r.text[:500] for k in ['"sequences"', '"items"', '"@context"'])
        if is_iiif:
            import json
            d = r.json()
            canvases = len(d.get('sequences', [{}])[0].get('canvases', d.get('items', [])))
            label = str(d.get('label', ''))[:60]
            print(f"  [OK-IIIF] {nome}")
            print(f"    canvases={canvases} | {label}")
            print(f"    url={manifest_url}")
        else:
            print(f"  [{r.status_code}] {nome} - non IIIF o non raggiungibile")
    except Exception as e:
        print(f"  [ERR] {nome}: {type(e).__name__}")
