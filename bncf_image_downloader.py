import os
import requests
from tqdm import tqdm

# Configurazione utente
IDR = "BNCF00004140910"  # Cambia con l'ID desiderato
OUTPUT_DIR = "bncf_download"
MODALITA = "R"  # "R" per registro (tutte le pagine), "D" per documento singolo
SEQUENCE_START = 1  # Prima pagina (inclusa)
SEQUENCE_END = None  # Ultima pagina (inclusa), None per auto-detect in modalità R
SINGLE_SEQUENCE = 1  # Usato solo in modalità D

BASE_URL = "https://teca.bncf.firenze.sbn.it/ImageViewer/servlet/ImageViewer"

os.makedirs(OUTPUT_DIR, exist_ok=True)

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36"
}

def download_image(idr, sequence, out_dir):
    params = {
        "idr": idr,
        "azione": "showImg",
        "sequence": sequence,
        "reduce": 0
    }
    resp = requests.get(BASE_URL, params=params, headers=headers, stream=True)
    if resp.status_code == 200 and resp.headers.get("Content-Type", "").startswith("image"):
        filename = os.path.join(out_dir, f"{idr}_page_{sequence}.jpg")
        with open(filename, "wb") as f:
            for chunk in resp.iter_content(1024):
                f.write(chunk)
        return True
    return False

def download_registro(idr, out_dir, seq_start=1, seq_end=None):
    sequence = seq_start
    found = 0
    pbar = tqdm(disable=True)
    while True:
        if seq_end is not None and sequence > seq_end:
            break
        ok = download_image(idr, sequence, out_dir)
        if not ok:
            if seq_end is None:
                break  # Fine registro
            else:
                print(f"[!] Pagina {sequence} non trovata")
        else:
            found += 1
            print(f"Scaricata pagina {sequence}")
        sequence += 1
    print(f"Totale immagini scaricate: {found}")

def download_documento(idr, out_dir, sequence=1):
    ok = download_image(idr, sequence, out_dir)
    if ok:
        print(f"Scaricata pagina {sequence}")
    else:
        print(f"[!] Pagina {sequence} non trovata")

if __name__ == "__main__":
    if MODALITA.upper() == "R":
        download_registro(IDR, OUTPUT_DIR, SEQUENCE_START, SEQUENCE_END)
    elif MODALITA.upper() == "D":
        download_documento(IDR, OUTPUT_DIR, SINGLE_SEQUENCE)
    else:
        print("Modalità non riconosciuta. Usa 'R' o 'D'.")
