"""
run_genealogy_1841.py — Estrazione genealogica batch: Stati delle Anime Elci 1841
Usa ATK-Pro v3.0 + Gemini (chiave dal Caveau api_keys.csv).

Uso:
    .venv312\Scripts\python.exe run_genealogy_1841.py
    .venv312\Scripts\python.exe run_genealogy_1841.py --da 3 --a 6   # solo immagini 3-6
    .venv312\Scripts\python.exe run_genealogy_1841.py --da 3 --a 6 --provider Claude
"""
import os
import sys
import json
import argparse

# ── Path ──────────────────────────────────────────────────────────────────────
ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(ROOT, "src"))

from PySide6.QtCore import QCoreApplication
from genealogy_dialog import GenealogyWorker

# ── Configurazione ────────────────────────────────────────────────────────────

# Cartella sorgente immagini (canvas TIF prodotti dalla scansione)
SRC_DIR = r"C:\Users\danie\OneDrive\Documenti\ATK-Pro\output\LD2xzdG_Test_Enrico_Davini"

# Output nella stessa cartella sorgente (così il merge funziona su riesecuzione)
OUT_FILE = os.path.join(SRC_DIR, "poncarale_1841_integrale.ged")

# Immagini disponibili: canvas 1-13 (1=copertina, 2=frontespizio → si possono saltare)
ALL_IMAGES = [
    os.path.join(SRC_DIR, f"Test Enrico Davini_canvas_{i}.tif")
    for i in range(1, 14)
]

PROVIDER = "Gemini"     # Gemini | Claude | OpenAI
DOC_TYPE = "Stati delle Anime Granducato di Toscana"

# Carica il preset con le dritte paleografiche locali
_PRESETS_FILE = os.path.join(ROOT, "genealogy_presets.json")
PRESET_KEY = "Stati delle Anime Elci Montalbano S.Lorenzo 1841"
try:
    with open(_PRESETS_FILE, "r", encoding="utf-8") as f:
        _presets = json.load(f)
    TIPS = _presets.get(PRESET_KEY, "")
    print(f"[OK] Preset '{PRESET_KEY}' caricato ({len(TIPS)} caratteri).")
except Exception as e:
    print(f"[WARN] Preset non trovato: {e}")
    TIPS = ""

# ── Argomenti CLI ─────────────────────────────────────────────────────────────
parser = argparse.ArgumentParser(description="Estrazione genealogica batch 1841")
parser.add_argument("--da",       type=int, default=1,        help="Prima immagine (1-based)")
parser.add_argument("--a",        type=int, default=13,       help="Ultima immagine (1-based, inclusa)")
parser.add_argument("--provider", type=str, default=PROVIDER, help="Provider IA (Gemini/Claude/OpenAI)")
parser.add_argument("--out",      type=str, default=OUT_FILE,  help="Path file .ged di output")
args = parser.parse_args()

images = [img for img in ALL_IMAGES if os.path.exists(img)]
images = [img for img in images
          if int(os.path.basename(img).split("_canvas_")[1].split(".")[0]) >= args.da
          and int(os.path.basename(img).split("_canvas_")[1].split(".")[0]) <= args.a]

if not images:
    print(f"[ERRORE] Nessuna immagine trovata in: {SRC_DIR}")
    print(f"         Canvas {args.da}-{args.a}")
    sys.exit(1)

print(f"\n{'='*60}")
print(f"  ATK-Pro v3.0 — Estrazione Stato delle Anime 1841")
print(f"{'='*60}")
print(f"  Provider : {args.provider}")
print(f"  Immagini : {len(images)}  (canvas {args.da}-{args.a})")
print(f"  Output   : {args.out}")
print(f"  Merge    : {'SI (file esistente)' if os.path.exists(args.out) else 'NO (nuovo file)'}")
print(f"{'='*60}\n")

# ── Qt event loop ─────────────────────────────────────────────────────────────
app = QCoreApplication(sys.argv)

worker = GenealogyWorker(
    files=images,
    doc_type=DOC_TYPE,
    tips=TIPS,
    provider=args.provider,
    output_file_path=args.out,
)

def on_finished(path, count):
    base = os.path.splitext(path)[0]
    print(f"\n{'='*60}")
    print(f"  ESTRAZIONE COMPLETATA")
    print(f"{'='*60}")
    print(f"  GED             : {path}")
    print(f"  Registro orig.  : {base}_REGISTRO_ORIGINALE.csv")
    print(f"  Revisione gen.  : {base}_REVISIONE_GENEALOGICA.csv")
    print(f"  Record estratti : {count}")
    print(f"{'='*60}\n")
    app.quit()

def on_error(msg):
    print(f"\n[ERRORE IA] {msg}")
    app.quit()

def on_progress(pct, msg):
    bar_w = 30
    filled = int(bar_w * pct / 100)
    bar = "█" * filled + "░" * (bar_w - filled)
    sys.stdout.write(f"\r  [{bar}] {pct:3d}%  {msg[:50]:<50}")
    sys.stdout.flush()

worker.finished.connect(on_finished)
worker.error.connect(on_error)
worker.progress.connect(on_progress)

worker.start()
app.exec()
