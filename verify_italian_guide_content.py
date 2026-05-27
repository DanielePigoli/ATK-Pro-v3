#!/usr/bin/env python3
"""Check Italian guide files for stale v2/future-module wording."""

from __future__ import annotations

import re
import sys
import html as html_lib
from pathlib import Path


ROOT = Path(__file__).resolve().parent
GUIDE_DIR = ROOT / "assets" / "it" / "testuali"
AUDIT_FILE = ROOT / "docs_generali" / "audit_contenuti_guida_v3_ATK-Pro.md"
TRANSLATION_DIALOG = ROOT / "src" / "translation_dialog.py"

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

GUIDE_INDEX_MODULES = [
    "guida_01_installazione_configurazione.html",
    "guida_02_operazioni_base.html",
    "guida_03_visualizzazione_immagini.html",
    "guida_04_visualizzazione_metadati.html",
    "guida_05_ocr_avanzato.html",
    "guida_06_traduzione.html",
    "guida_07_esportazione_gedcom.html",
    "guida_08_supporto_faq.html",
    "guida_09_ricerca_assistita_ai.html",
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
    re.compile(r"input_link_base_v2\.0\.txt", re.IGNORECASE),
    re.compile(r"input_link_base_\.txt", re.IGNORECASE),
    re.compile(r"Guida operativa completa \(12 sezioni\)", re.IGNORECASE),
    re.compile(r"serie versioni \(1\.x, 2\.x, 3\.x, 4\.x, 5\.x\)", re.IGNORECASE),
    re.compile(r"Milestones: Python puro", re.IGNORECASE),
    re.compile(r"registry portali", re.IGNORECASE),
]

TRANSLATION_TARGET_AUTONYMS = [
    "Italiano", "English", "Español", "Français", "Deutsch", "Português",
    "Русский", "العربية", "Nederlands", "עברית", "日本語", "中文",
    "Polski", "Türkçe", "Dansk", "Norsk", "Tiếng Việt", "Ελληνικά",
    "Română", "Svenska",
]

UNSUPPORTED_TRANSLATION_TARGETS = [
    "한국어",
    "हिन्दी",
    "Čeština",
    "Suomi",
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


def visible_body_text(html: str) -> str:
    body_start = html.lower().find("<body")
    if body_start != -1:
        html = html[body_start:]
    html = re.sub(r"<script\b.*?</script>", " ", html, flags=re.IGNORECASE | re.DOTALL)
    html = re.sub(r"<style\b.*?</style>", " ", html, flags=re.IGNORECASE | re.DOTALL)
    html = re.sub(r"<[^>]+>", " ", html)
    return html_lib.unescape(re.sub(r"\s+", " ", html).strip())


def check_guide_index() -> list[str]:
    issues: list[str] = []
    path = GUIDE_DIR / "guida.html"
    if not path.is_file():
        return [f"{path.relative_to(ROOT)}: missing file"]

    html = path.read_text(encoding="utf-8", errors="replace")
    for module in GUIDE_INDEX_MODULES:
        if f'href="{module}"' not in html:
            issues.append(f"{path.relative_to(ROOT)}: missing module link {module}")

    text = visible_body_text(html)
    if len(text) > 9000:
        issues.append(
            f"{path.relative_to(ROOT)}: guide index is too long ({len(text)} visible chars); "
            "keep detailed content in module files"
        )

    duplicated_section_markers = [
        "1. INSTALLAZIONE E REQUISITI",
        "4. CARICAMENTO RECORD IIIF",
        "5. ELABORAZIONE E DOWNLOAD IMMAGINI",
        "12. TROUBLESHOOTING E FAQ",
    ]
    for marker in duplicated_section_markers:
        if marker in html:
            issues.append(f"{path.relative_to(ROOT)}: duplicated full-guide marker '{marker}'")

    return issues


def check_translation_targets() -> list[str]:
    issues: list[str] = []
    guide_path = GUIDE_DIR / "guida_06_traduzione.html"
    dialog_text = TRANSLATION_DIALOG.read_text(encoding="utf-8", errors="replace")
    guide_text = visible_body_text(guide_path.read_text(encoding="utf-8", errors="replace"))

    for autonym in TRANSLATION_TARGET_AUTONYMS:
        if autonym not in dialog_text:
            issues.append(f"{TRANSLATION_DIALOG.relative_to(ROOT)}: missing target language {autonym}")
        if autonym not in guide_text:
            issues.append(f"{guide_path.relative_to(ROOT)}: missing target language {autonym}")

    for autonym in UNSUPPORTED_TRANSLATION_TARGETS:
        if autonym in dialog_text:
            issues.append(f"{TRANSLATION_DIALOG.relative_to(ROOT)}: unsupported target language {autonym}")
        if autonym in guide_text:
            issues.append(f"{guide_path.relative_to(ROOT)}: unsupported target language {autonym}")

    return issues


def main() -> int:
    issues: list[str] = []
    for path in CHECK_FILES:
        issues.extend(check_file(path))
    issues.extend(check_guide_index())
    issues.extend(check_translation_targets())

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
