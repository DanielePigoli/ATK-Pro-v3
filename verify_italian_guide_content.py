#!/usr/bin/env python3
"""Check Italian guide files for stale v2/future-module wording."""

from __future__ import annotations

import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent
GUIDE_DIR = ROOT / "assets" / "it" / "testuali"
AUDIT_FILE = ROOT / "docs_generali" / "audit_contenuti_guida_v3_ATK-Pro.md"

CHECK_FILES = [
    GUIDE_DIR / "guida.html",
    GUIDE_DIR / "guida_01_installazione_configurazione.html",
    GUIDE_DIR / "guida_02_operazioni_base.html",
    GUIDE_DIR / "guida_03_visualizzazione_immagini.html",
    GUIDE_DIR / "guida_04_visualizzazione_metadati.html",
    GUIDE_DIR / "guida_05_ocr_avanzato.html",
    GUIDE_DIR / "guida_06_traduzione.html",
    GUIDE_DIR / "guida_07_esportazione_gedcom.html",
    GUIDE_DIR / "guida_08_supporto_faq.html",
    GUIDE_DIR / "guida_09_ricerca_assistita_ai.html",
    AUDIT_FILE,
]

STALE_PATTERNS = [
    re.compile(r"non e' ancora pronta", re.IGNORECASE),
    re.compile(r"release candidate deve quindi restare bloccata", re.IGNORECASE),
    re.compile(r"\bStrumenti\b", re.IGNORECASE),
    re.compile(r"servizi placeholder", re.IGNORECASE),
    re.compile(r"placeholder \(Sezione 8\)", re.IGNORECASE),
    re.compile(r"Pianificato per versioni future", re.IGNORECASE),
    re.compile(r"funzione in sviluppo", re.IGNORECASE),
    re.compile(r"una volta sviluppato", re.IGNORECASE),
    re.compile(r"bozza ipotetica", re.IGNORECASE),
    re.compile(r"\bv2\.[123]\b", re.IGNORECASE),
    re.compile(r"GPT-4o costa", re.IGNORECASE),
    re.compile(r"Claude 3\.5", re.IGNORECASE),
]


def is_allowed_placeholder(line: str) -> bool:
    lower = line.lower()
    return "pagina" in lower and "placeholder" in lower and "canvas" in lower


def check_file(path: Path) -> list[str]:
    issues: list[str] = []
    if not path.is_file():
        return [f"{path.relative_to(ROOT)}: missing file"]

    for lineno, line in enumerate(path.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
        if "placeholder" in line.lower() and is_allowed_placeholder(line):
            continue
        for pattern in STALE_PATTERNS:
            if pattern.search(line):
                issues.append(f"{path.relative_to(ROOT)}:{lineno}: stale marker: {pattern.pattern}")
    return issues


def main() -> int:
    issues: list[str] = []
    for path in CHECK_FILES:
        issues.extend(check_file(path))

    if issues:
        print("Italian guide content verification failed:")
        for issue in issues:
            print(f"- {issue}")
        return 1

    print("Italian guide content markers are clean.")
    print(f"- Files checked: {len(CHECK_FILES)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
