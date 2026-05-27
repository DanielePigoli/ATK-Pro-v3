#!/usr/bin/env python3
"""Verify menu document assets and local links for every packaged language."""

from __future__ import annotations

import re
import sys
from pathlib import Path
from urllib.parse import unquote, urlsplit


ROOT = Path(__file__).resolve().parent
ASSETS_DIR = ROOT / "assets"
EXAMPLE_INPUT_FILE = "input_link_base.txt"
OLD_EXAMPLE_INPUT_FILES = (
    "input_link_base_v2.0.txt",
    "input_link_base_.txt",
)

GUIDE_MODULES = [
    "guida_01_installazione_configurazione.html",
    "guida_02_operazioni_base.html",
    "guida_03_visualizzazione_immagini.html",
    "guida_04_visualizzazione_metadati.html",
    "guida_05_ocr_avanzato.html",
    "guida_06_traduzione.html",
    "guida_07_esportazione_gedcom.html",
    "guida_08_supporto_faq.html",
]

MENU_DOCUMENTS = {
    "Disclaimer": (
        "disclaimer_legale_ATK-Pro.html",
        "disclaimer_legale_ATK-Pro.txt",
    ),
    "Presentazione autore": (
        "presentazione_autore.html",
        "presentazione_autore.txt",
    ),
    "Presentazione progetto": (
        "presentazione_progetto_ATK-Pro.html",
        "presentazione_progetto_ATK-Pro.md",
    ),
    "Guida": (
        "guida.html",
        "guida.txt",
    ),
}

LOCAL_REF_RE = re.compile(
    r"""(?ix)
    \b(?:href|src)\s*=\s*["']([^"']+)["']
    |
    \burl\(\s*["']?([^"')]+)["']?\s*\)
    """
)


def language_dirs() -> list[Path]:
    return sorted(path for path in ASSETS_DIR.iterdir() if path.is_dir() and path.name != "common")


def is_external_or_inline(ref: str) -> bool:
    value = ref.strip()
    lower = value.lower()
    if not value or value.startswith("#"):
        return True
    return lower.startswith(("http://", "https://", "mailto:", "data:", "javascript:", "tel:"))


def resolve_local_ref(base_file: Path, ref: str) -> Path:
    path_part = urlsplit(ref).path
    return (base_file.parent / unquote(path_part)).resolve()


def local_refs(html_path: Path) -> list[str]:
    text = html_path.read_text(encoding="utf-8", errors="replace")
    refs: list[str] = []
    for match in LOCAL_REF_RE.finditer(text):
        ref = match.group(1) or match.group(2) or ""
        if not is_external_or_inline(ref):
            refs.append(ref)
    return refs


def check_menu_documents(lang_dir: Path) -> list[str]:
    issues: list[str] = []
    text_dir = lang_dir / "testuali"
    for label, alternatives in MENU_DOCUMENTS.items():
        if not any((text_dir / filename).is_file() for filename in alternatives):
            issues.append(f"{lang_dir.name}: missing menu document '{label}' ({', '.join(alternatives)})")
    return issues


def check_example_input(lang_dir: Path) -> list[str]:
    issues: list[str] = []
    text_dir = lang_dir / "testuali"
    if not (text_dir / EXAMPLE_INPUT_FILE).is_file():
        issues.append(f"{lang_dir.name}: missing example input file {EXAMPLE_INPUT_FILE}")
    for old_name in OLD_EXAMPLE_INPUT_FILES:
        if (text_dir / old_name).exists():
            issues.append(f"{lang_dir.name}: obsolete example input file still present: {old_name}")
    return issues


def check_obsolete_example_references(lang_dir: Path) -> list[str]:
    issues: list[str] = []
    text_dir = lang_dir / "testuali"
    for path in sorted(text_dir.glob("*")):
        if path.suffix.lower() not in {".html", ".txt", ".md"}:
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        for old_name in OLD_EXAMPLE_INPUT_FILES:
            if old_name in text:
                issues.append(f"{path.relative_to(ROOT)}: obsolete example input reference: {old_name}")
    return issues


def check_guide_set(lang_dir: Path) -> list[str]:
    issues: list[str] = []
    text_dir = lang_dir / "testuali"

    guide_index = text_dir / "guida.html"
    if not guide_index.is_file():
        issues.append(f"{lang_dir.name}: missing guida.html")
        return issues

    for module in GUIDE_MODULES:
        module_path = text_dir / module
        if not module_path.is_file():
            issues.append(f"{lang_dir.name}: missing guide module {module}")
            continue
        if module not in guide_index.read_text(encoding="utf-8", errors="replace"):
            issues.append(f"{lang_dir.name}: guida.html does not link {module}")

    return issues


def check_local_links(lang_dir: Path) -> list[str]:
    issues: list[str] = []
    text_dir = lang_dir / "testuali"
    html_files = sorted(text_dir.glob("*.html"))

    for html_path in html_files:
        for ref in local_refs(html_path):
            target = resolve_local_ref(html_path, ref)
            try:
                target.relative_to(ROOT.resolve())
            except ValueError:
                issues.append(f"{html_path.relative_to(ROOT)}: local reference escapes repository: {ref}")
                continue
            if not target.exists():
                issues.append(f"{html_path.relative_to(ROOT)}: missing local reference: {ref}")

    return issues


def main() -> int:
    issues: list[str] = []
    langs = language_dirs()

    if not langs:
        print("ERROR: no language asset directories found", file=sys.stderr)
        return 1

    common_required = [
        ASSETS_DIR / "common" / "grafici" / "Sfondo.webp",
        ASSETS_DIR / "common" / "grafici" / "ATK-Pro.ico",
        ASSETS_DIR / "common" / "testuali" / "email.txt",
    ]
    for path in common_required:
        if not path.is_file():
            issues.append(f"missing common asset: {path.relative_to(ROOT)}")

    for lang_dir in langs:
        issues.extend(check_menu_documents(lang_dir))
        issues.extend(check_example_input(lang_dir))
        issues.extend(check_obsolete_example_references(lang_dir))
        issues.extend(check_guide_set(lang_dir))
        issues.extend(check_local_links(lang_dir))

    if issues:
        print("Document asset verification failed:")
        for issue in issues:
            print(f"- {issue}")
        return 1

    print("Document assets are complete and locally linked.")
    print(f"- Languages checked: {len(langs)}")
    print(f"- Guide modules per language: {len(GUIDE_MODULES)}")
    print("- Menu documents checked: Disclaimer, author, project, guide")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
