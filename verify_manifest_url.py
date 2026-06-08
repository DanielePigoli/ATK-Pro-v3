from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.manifest_utils import download_manifest


DEFAULT_OUTPUT_DIR = ROOT / ".codex_tmp" / "manifest_url_probe"


def canvas_count(manifest: Any) -> int:
    if not isinstance(manifest, dict):
        return 0

    sequences = manifest.get("sequences")
    if isinstance(sequences, list) and sequences:
        canvases = sequences[0].get("canvases")
        if isinstance(canvases, list):
            return len(canvases)

    items = manifest.get("items")
    if isinstance(items, list):
        return len(items)

    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Verifica prudente di un manifest IIIF diretto: scarica il JSON e conta canvas/items."
    )
    parser.add_argument("--url", required=True, help="URL diretto del manifest IIIF da verificare.")
    parser.add_argument("--referer", help="Referer da inviare, se richiesto dal portale.")
    parser.add_argument("--title", default="manifest_probe", help="Titolo base per il file salvato.")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR, help="Cartella report/manifest.")
    args = parser.parse_args(argv)

    manifest = download_manifest(
        args.url,
        str(args.output_dir),
        args.title,
        referer=args.referer,
    )
    if not manifest:
        print("FAIL Manifest non scaricato o non valido.")
        return 1

    count = canvas_count(manifest)
    if count <= 0:
        print("FAIL Manifest scaricato, ma nessun canvas/item rilevato.")
        return 1

    print(f"PASS Manifest scaricato e valido. Canvas/items: {count}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
