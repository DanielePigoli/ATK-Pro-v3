#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Localization verification script for ATK‑Pro v3.0

It checks:
1. The glossario JSON contains entries for all supported languages.
2. .po/.pot files exist for each language.
3. All calls to get_msg in *.py pass a valid language code.
4. UI strings are sourced via get_msg (no hard‑coded literals).
5. The HTML generation script can render the glossary.

The script produces a report file `localization_check_report.txt` and prints a
summary to stdout.
"""
import os
import json
import re
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
SUPPORTED_LANGUAGES = [
    "IT", "EN", "ES", "FR", "DE", "PT", "RU", "AR", "NL", "HE", "JA", "SV", "ZH", "RO", "EL", "PL", "DA", "NO", "TR", "VI"
]

PROJECT_ROOT = Path(__file__).resolve().parent
GLOSSARY_PATH = PROJECT_ROOT / "docs_generali" / "glossario_multilingua_ATK-Pro.json"
REPORT_PATH = PROJECT_ROOT / "localization_check_report.txt"

# Helper to write report lines
report_lines = []

def add(line: str):
    report_lines.append(line)
    print(line)

def load_glossary(path: Path):
    raw = path.read_text(encoding="utf-8")
    first_brace = raw.find("{")
    if first_brace != -1:
        raw = raw[first_brace:]
    return json.loads(raw)

# ---------------------------------------------------------------------------
# 1. Load glossario JSON and verify language coverage
# ---------------------------------------------------------------------------
if not GLOSSARY_PATH.is_file():
    add(f"[ERROR] Glossario JSON not found at {GLOSSARY_PATH}")
else:
    try:
        glossario = load_glossary(GLOSSARY_PATH)
    except Exception as e:
        add(f"[ERROR] Failed to parse glossario JSON: {e}")
        glossario = {}
    missing_entries = []
    for section, entries in glossario.items():
        if not isinstance(entries, list):
            continue
        for idx, entry in enumerate(entries):
            if not isinstance(entry, dict):
                continue
            for lang in SUPPORTED_LANGUAGES:
                if lang not in entry:
                    missing_entries.append((f"{section}[{idx}]", lang))
    if missing_entries:
        add("[WARN] Missing translations in glossario_multilingua_ATK-Pro.json:")
        for k, l in missing_entries:
            add(f"  - key '{k}' missing language '{l}'")
    else:
        add("[OK] All glossary entries contain every supported language.")

# ---------------------------------------------------------------------------
# 2. Verify .po/.pot files for each language (if locales folder exists)
# ---------------------------------------------------------------------------
LOCALES_DIR = PROJECT_ROOT / "locales"
if LOCALES_DIR.is_dir():
    po_files = list(LOCALES_DIR.rglob("*.po"))
    pot_files = list(LOCALES_DIR.rglob("*.pot"))
    existing_langs = set()
    for p in po_files:
        lang_dir = p.parent.parent.name
        if re.match(r"^[a-z]{2}(?:_[A-Z]{2})?$", lang_dir):
            existing_langs.add(lang_dir[:2].upper())
    if pot_files:
        existing_langs.add("POT")
    missing_langs = [l for l in SUPPORTED_LANGUAGES if l not in existing_langs]
    if missing_langs:
        add("[WARN] Missing .po/.pot translation files for languages:")
        for l in missing_langs:
            add(f"  - {l}")
    else:
        add("[OK] Translation files for all supported languages are present.")
else:
    add("[INFO] No 'locales' directory – skipping .po/.pot checks.")

# ---------------------------------------------------------------------------
# 3. Scan Python sources for get_msg usage and language handling
# ---------------------------------------------------------------------------
SKIP_DIRS = {
    ".git", ".venv312", ".pytest_cache", "__pycache__", "build", "dist",
    "_win_artifacts", "tmp", "Backups", "Output", "scratch"
}
PY_FILES = [
    path for path in PROJECT_ROOT.rglob("*.py")
    if not (set(path.relative_to(PROJECT_ROOT).parts) & SKIP_DIRS)
]
invalid_get_msg_calls = []
for py in PY_FILES:
    try:
        content = py.read_text(encoding="utf-8")
    except Exception:
        continue
    for match in re.finditer(r"get_msg\s*\(([^)]+)\)", content):
        args = match.group(1).split(",")
        if len(args) < 3:
            continue  # not enough args to contain language
        lang_arg = args[2].strip()
        # Accept literals like "IT" or variable – if variable, we cannot ensure value.
        if re.match(r"^[\'\"]([A-Za-z]{2})[\'\"]$", lang_arg):
            lang_code = re.findall(r"[A-Za-z]{2}", lang_arg)[0].upper()
            if lang_code not in SUPPORTED_LANGUAGES:
                invalid_get_msg_calls.append((py, match.start()))
        # If it's a variable, we assume it will be validated elsewhere.

if invalid_get_msg_calls:
    add("[WARN] get_msg calls with unsupported language literals:")
    for file_path, pos in invalid_get_msg_calls:
        add(f"  - {file_path} (pos {pos})")
else:
    add("[OK] All get_msg calls use supported language literals or variables.")

# ---------------------------------------------------------------------------
# 4. Detect hard‑coded UI strings (simple heuristic)
# ---------------------------------------------------------------------------
hard_coded_strings = []
UI_STRING_PATTERN = re.compile(r"QPushButton\s*\(\s*\'([^\']+)\'\s*\)")
SRC_FILES = [path for path in (PROJECT_ROOT / "src").rglob("*.py")]
SYMBOL_ONLY = re.compile(r"^\s*(self\.)?\w+\s*=\s*QPushButton\([\"']\s*[\W_]{1,4}\s*[\"']\)")
UI_CONSTANT_ONLY = re.compile(
    r"^\s*(?:self\.)?\w+\s*=\s*(?:QPushButton|QLabel)\(\s*[\"']\s*[-+−/0-9:%.\s]+\s*[\"']\s*\)"
)
PAGE_COUNTER_ONLY = re.compile(r"QLabel\(\s*f[\"']\s*/\s*\{[^}]+\}\s*[\"']\s*\)")

def localized_variable_messagebox(line: str) -> bool:
    """Allow message boxes assembled only from localized variables and punctuation."""
    match = re.search(
        r"QMessageBox\.\w+\([^,]+,\s*[A-Za-z_]\w*,\s*f([\"'])(.*)\1\s*\)",
        line,
    )
    if not match:
        return False
    body = re.sub(r"\{[^}]+\}", "", match.group(2))
    body = re.sub(r"\\[nrt]", "", body)
    return not re.search(r"[A-Za-zÀ-ÿ]", body)

for py in SRC_FILES:
    try:
        lines = py.read_text(encoding="utf-8").splitlines()
    except Exception:
        continue
    for i, line in enumerate(lines, start=1):
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "setStyleSheet" in stripped:
            continue
        if (
            "QPushButton#" in stripped
            or "QPushButton {" in stripped
            or SYMBOL_ONLY.match(stripped)
            or UI_CONSTANT_ONLY.match(stripped)
            or PAGE_COUNTER_ONLY.search(stripped)
            or localized_variable_messagebox(stripped)
        ):
            continue
        # Look for literal strings passed to widget constructors
        if "QPushButton" in line or "QLabel" in line or "QMessageBox" in line:
            if ("'" in line or '"' in line) and "get_msg" not in line and ".gm(" not in line and "_gm(" not in line:
                hard_coded_strings.append((py, i, stripped))
        # also check .ui files for literal text

if hard_coded_strings:
    add("[WARN] Possible hard-coded UI strings (should be localized via get_msg):")
    for file_path, ln, txt in hard_coded_strings:
        add(f"  - {file_path}:{ln} -> {txt}")
else:
    add("[OK] No obvious hard-coded UI strings found.")

# ---------------------------------------------------------------------------
# 5. Verify HTML generation script (if present)
# ---------------------------------------------------------------------------
HTML_GEN_SCRIPT = PROJECT_ROOT / "generate_glossary_html.py"
if HTML_GEN_SCRIPT.is_file():
    try:
        import subprocess
        result = subprocess.run([sys.executable, str(HTML_GEN_SCRIPT)],
                                cwd=str(PROJECT_ROOT), capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            add("[OK] HTML generation script executed successfully.")
        else:
            add("[WARN] HTML generation script returned non-zero exit code.")
            add(f"      stderr: {result.stderr.strip()}")
    except Exception as e:
        add(f"[ERROR] Failed to run HTML generation script: {e}")
else:
    add("[INFO] No generate_glossary_html.py script – skipping HTML generation check.")

# ---------------------------------------------------------------------------
# Write report file
# ---------------------------------------------------------------------------
with open(REPORT_PATH, "w", encoding="utf-8") as f:
    f.write("\n".join(report_lines))
add(f"\nReport written to {REPORT_PATH}\n")

sys.exit(0)
