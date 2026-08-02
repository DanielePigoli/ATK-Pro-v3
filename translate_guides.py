#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Preparazione controllata delle localizzazioni documentali di ATK-Pro.

Senza ``--execute`` lo script svolge soltanto un audit: non carica chiavi API,
non effettua chiamate esterne e non scrive file. Con ``--execute`` genera i
documenti in ``localization_staging``; non modifica mai ``assets``.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import sys
import time
from typing import Any


if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")


PROJECT_ROOT = Path(__file__).resolve().parent
ASSETS_DIR = PROJECT_ROOT / "assets"
ITALIAN_DIR = ASSETS_DIR / "it" / "testuali"
DEFAULT_STAGING_ROOT = PROJECT_ROOT / "localization_staging"
CONFIG_FILE = PROJECT_ROOT / "config.json"

GUIDE_FILES = (
    "guida.html",
    "guida_01_installazione_configurazione.html",
    "guida_02_operazioni_base.html",
    "guida_03_ricerca_assistita_ai.html",
    "guida_04_visualizzazione_immagini.html",
    "guida_05_visualizzazione_metadati.html",
    "guida_06_ocr_avanzato.html",
    "guida_07_traduzione.html",
    "guida_08_esportazione_gedcom.html",
    "guida_09_supporto_faq.html",
)

PRESENTATION_FILES = (
    "presentazione_autore.html",
    "presentazione_progetto_ATK-Pro.html",
)

DISCLAIMER_FILES = (
    "disclaimer_legale_ATK-Pro.html",
    "disclaimer_legale_ATK-Pro.txt",
)

DOCUMENT_FILES = GUIDE_FILES + PRESENTATION_FILES + DISCLAIMER_FILES

# codice: (nome usato nel prompt, attributo HTML lang, direzione)
LANGUAGES = {
    "ar": ("Arabic", "ar", "rtl"),
    "da": ("Danish", "da", "ltr"),
    "de": ("German", "de", "ltr"),
    "el": ("Greek", "el", "ltr"),
    "en": ("English", "en", "ltr"),
    "es": ("Spanish", "es", "ltr"),
    "fr": ("French", "fr", "ltr"),
    "he": ("Hebrew", "he", "rtl"),
    "ja": ("Japanese", "ja", "ltr"),
    "nl": ("Dutch", "nl", "ltr"),
    "no": ("Norwegian", "no", "ltr"),
    "pl": ("Polish", "pl", "ltr"),
    "pt": ("Portuguese", "pt", "ltr"),
    "ro": ("Romanian", "ro", "ltr"),
    "ru": ("Russian", "ru", "ltr"),
    "sv": ("Swedish", "sv", "ltr"),
    "tr": ("Turkish", "tr", "ltr"),
    "vi": ("Vietnamese", "vi", "ltr"),
    "zh": ("Chinese (Simplified)", "zh", "ltr"),
}

DO_NOT_TRANSLATE = (
    "ATK-Pro",
    "Antenati Toolkit Pro",
    "Portale Antenati",
    "GNU Affero General Public License",
    "AGPL-3.0-or-later",
    "Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International",
    "CC BY-NC-SA 4.0",
    "GEDCOM",
    "TEI",
    "IIIF",
    "OCR",
    "LLM",
    "Gemini",
    "GPT-4o",
    "Claude",
    "Google",
    "OpenAI",
    "Anthropic",
    "XML",
    "JSON",
    "HTML",
    "DOCX",
    "PDF",
    "PNG",
    "JPG",
    "TIFF",
    "WebP",
    "EXIF",
    "API",
)

TRANSLATE_TAGS = {
    "title", "h1", "h2", "h3", "h4", "p", "li", "td", "th", "span",
    "a", "strong", "em", "button", "label", "caption", "dt", "dd",
    "figcaption", "blockquote", "pre",
}
SKIP_TAGS = {"style", "script", "code"}
PLACEHOLDER_RE = re.compile(r"\{(T\d{5})\}")
LINK_RE = re.compile(r'href=["\']([^"\']+\.html)["\']', re.IGNORECASE)


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def should_translate(text: str) -> bool:
    value = text.strip()
    if len(value) < 2 or re.fullmatch(r"[\s\d\W]+", value):
        return False
    if re.match(r"https?://", value) or re.match(r"^mailto:", value):
        return False
    if re.fullmatch(r"[\w.-]+@[\w.-]+", value):
        return False
    if re.fullmatch(r"[a-z0-9_.-]+\.(?:html|txt|webp|png|jpg|css|js)", value, re.I):
        return False
    return bool(re.search(r"[A-Za-zÀ-ÿ]", value))


def extract_html_text(html: str) -> tuple[str, dict[str, str]]:
    """Sostituisce esclusivamente i nodi testuali traducibili con segnaposto."""
    parts = re.split(r"(<[^>]*?>)", html, flags=re.DOTALL)
    texts: dict[str, str] = {}
    stack: list[str] = []
    skip_depth = 0
    result: list[str] = []

    for index, segment in enumerate(parts):
        if index % 2:
            match = re.match(r"</?([a-zA-Z][a-zA-Z0-9]*)", segment)
            if match:
                tag = match.group(1).lower()
                closing = segment.startswith("</")
                self_closing = segment.rstrip().endswith("/>")
                if closing:
                    if tag in SKIP_TAGS and skip_depth:
                        skip_depth -= 1
                    for position in range(len(stack) - 1, -1, -1):
                        if stack[position] == tag:
                            stack.pop(position)
                            break
                elif not self_closing:
                    if tag in SKIP_TAGS:
                        skip_depth += 1
                    stack.append(tag)
            result.append(segment)
            continue

        stripped = segment.strip()
        if skip_depth or not any(tag in TRANSLATE_TAGS for tag in stack) or not should_translate(stripped):
            result.append(segment)
            continue
        placeholder = f"T{len(texts):05d}"
        texts[placeholder] = stripped
        leading = segment[: len(segment) - len(segment.lstrip())]
        trailing = segment[len(segment.rstrip()) :]
        result.append(f"{leading}{{{placeholder}}}{trailing}")

    return "".join(result), texts


def extract_plain_text(text: str) -> tuple[str, dict[str, str]]:
    """Tratta ogni riga non vuota del disclaimer TXT come unità controllata."""
    texts: dict[str, str] = {}
    result: list[str] = []
    for line in text.splitlines(keepends=True):
        ending = "\r\n" if line.endswith("\r\n") else "\n" if line.endswith("\n") else ""
        value = line[: -len(ending)] if ending else line
        if should_translate(value):
            placeholder = f"T{len(texts):05d}"
            texts[placeholder] = value
            result.append(f"{{{placeholder}}}{ending}")
        else:
            result.append(line)
    return "".join(result), texts


def apply_translations(template: str, source: dict[str, str], translated: dict[str, Any]) -> str:
    if set(translated) != set(source):
        missing = sorted(set(source) - set(translated))
        extra = sorted(set(translated) - set(source))
        raise ValueError(f"Segnaposto non allineati; mancanti={missing}, extra={extra}")
    if not all(isinstance(value, str) and value.strip() for value in translated.values()):
        raise ValueError("La risposta contiene traduzioni vuote o non testuali")
    rendered = PLACEHOLDER_RE.sub(lambda match: translated[match.group(1)], template)
    if PLACEHOLDER_RE.search(rendered):
        raise ValueError("Sono rimasti segnaposto non sostituiti")
    return rendered


def update_html_language(html: str, html_lang: str, direction: str) -> str:
    match = re.search(r"<html\b([^>]*)>", html, flags=re.IGNORECASE)
    if not match:
        raise ValueError("Elemento <html> non trovato")
    attributes = match.group(1)
    if re.search(r"\blang=[\"\'][^\"\']*[\"\']", attributes, flags=re.I):
        attributes = re.sub(
            r"\blang=[\"\'][^\"\']*[\"\']", f'lang="{html_lang}"', attributes,
            count=1, flags=re.I,
        )
    else:
        attributes += f' lang="{html_lang}"'
    if re.search(r"\bdir=[\"\'][^\"\']*[\"\']", attributes, flags=re.I):
        attributes = re.sub(
            r"\bdir=[\"\'][^\"\']*[\"\']", f'dir="{direction}"', attributes,
            count=1, flags=re.I,
        )
    else:
        attributes += f' dir="{direction}"'
    return html[: match.start()] + f"<html{attributes}>" + html[match.end() :]


def load_api_key() -> str:
    key = os.environ.get("ATK_PRO_GEMINI_API_KEY", "").strip()
    if key:
        return key
    if CONFIG_FILE.is_file():
        data = json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
        key = str(data.get("ocr_api_key", "")).strip()
    if not key:
        raise RuntimeError(
            "Chiave Gemini assente: impostare ATK_PRO_GEMINI_API_KEY o ocr_api_key in config.json"
        )
    return key


class GeminiTranslator:
    def __init__(self, model_name: str, delay_seconds: float) -> None:
        import google.generativeai as genai

        genai.configure(api_key=load_api_key())
        self.model = genai.GenerativeModel(model_name)
        self.delay_seconds = delay_seconds

    def translate(self, texts: dict[str, str], language_name: str) -> dict[str, str]:
        translated: dict[str, str] = {}
        keys = list(texts)
        for offset in range(0, len(keys), 40):
            chunk_keys = keys[offset : offset + 40]
            chunk = {key: texts[key] for key in chunk_keys}
            prompt = (
                f"Translate every JSON value from Italian to {language_name}.\n"
                "Return only one valid JSON object with exactly the same keys.\n"
                "Preserve meaning, paragraph function, punctuation, URLs, file names, "
                "HTML entities, symbols and legal precision.\n"
                f"Never translate these expressions: {', '.join(DO_NOT_TRANSLATE)}.\n"
                "Do not add qualifications such as informal translation or precedence "
                "of another language.\n\n"
                + json.dumps(chunk, ensure_ascii=False, indent=2)
            )
            response = self.model.generate_content(prompt)
            raw = getattr(response, "text", "").strip()
            raw = re.sub(r"^```(?:json)?\s*", "", raw)
            raw = re.sub(r"\s*```$", "", raw)
            result = json.loads(raw)
            if set(result) != set(chunk):
                raise ValueError("La risposta del provider non conserva i segnaposto del blocco")
            translated.update(result)
            if offset + 40 < len(keys):
                time.sleep(self.delay_seconds)
        return translated


def audit_sources() -> dict[str, dict[str, Any]]:
    report: dict[str, dict[str, Any]] = {}
    missing = [name for name in DOCUMENT_FILES if not (ITALIAN_DIR / name).is_file()]
    if missing:
        raise FileNotFoundError(f"Sorgenti italiane mancanti: {', '.join(missing)}")

    expected_links = set(GUIDE_FILES[1:])
    guide_html = (ITALIAN_DIR / "guida.html").read_text(encoding="utf-8")
    actual_links = {Path(link).name for link in LINK_RE.findall(guide_html)}
    absent_links = sorted(expected_links - actual_links)
    if absent_links:
        raise ValueError(f"Collegamenti mancanti dalla guida italiana: {absent_links}")

    for name in DOCUMENT_FILES:
        source = (ITALIAN_DIR / name).read_text(encoding="utf-8")
        _, texts = extract_html_text(source) if name.endswith(".html") else extract_plain_text(source)
        report[name] = {
            "sha256": sha256_text(source),
            "characters": len(source),
            "translation_units": len(texts),
        }
    return report


def resolve_languages(only: list[str] | None, from_language: str | None) -> list[str]:
    selected = list(LANGUAGES)
    if only:
        unknown = sorted(set(only) - set(LANGUAGES))
        if unknown:
            raise ValueError(f"Lingue non supportate: {', '.join(unknown)}")
        selected = [code for code in selected if code in only]
    if from_language:
        if from_language not in selected:
            raise ValueError("--from-lang deve appartenere alle lingue selezionate")
        selected = selected[selected.index(from_language) :]
    return selected


def safe_destination(staging_root: Path, language: str, filename: str) -> Path:
    root = staging_root.resolve()
    destination = (root / language / "testuali" / filename).resolve()
    if root == ASSETS_DIR.resolve() or ASSETS_DIR.resolve() in destination.parents:
        raise ValueError("La destinazione non può trovarsi dentro assets")
    if language == "it":
        raise ValueError("La sorgente italiana è protetta da scrittura")
    if root not in destination.parents:
        raise ValueError("Destinazione esterna all'area di revisione")
    return destination


def execute_translation(
    languages: list[str], staging_root: Path, model_name: str, delay_seconds: float,
    overwrite: bool,
) -> None:
    translator = GeminiTranslator(model_name, delay_seconds)
    manifest: dict[str, Any] = {
        "source_language": "it",
        "provider": "Gemini",
        "model": model_name,
        "documents": {},
    }
    for language in languages:
        language_name, html_lang, direction = LANGUAGES[language]
        for filename in DOCUMENT_FILES:
            source_path = ITALIAN_DIR / filename
            destination = safe_destination(staging_root, language, filename)
            if destination.exists() and not overwrite:
                raise FileExistsError(
                    f"File di staging già presente: {destination}; usare --overwrite-staging"
                )
            source = source_path.read_text(encoding="utf-8")
            template, texts = (
                extract_html_text(source) if filename.endswith(".html") else extract_plain_text(source)
            )
            translated = translator.translate(texts, language_name)
            rendered = apply_translations(template, texts, translated)
            if filename.endswith(".html"):
                rendered = update_html_language(rendered, html_lang, direction)
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_text(rendered, encoding="utf-8", newline="")
            manifest["documents"][f"{language}/{filename}"] = {
                "source_sha256": sha256_text(source),
                "output_sha256": sha256_text(rendered),
                "translation_units": len(texts),
            }
            print(f"OK  {language}/{filename}: {len(texts)} unità")

    manifest_path = staging_root.resolve() / "translation_manifest.json"
    manifest_path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(f"Manifest: {manifest_path}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Audita o prepara in staging i 14 documenti localizzati di ATK-Pro"
    )
    parser.add_argument("--only", nargs="+", help="Limita le lingue, es. --only en")
    parser.add_argument("--from-lang", help="Riprende dalla lingua indicata")
    parser.add_argument(
        "--execute", action="store_true",
        help="Autorizza chiamate Gemini e scrittura esclusivamente nello staging",
    )
    parser.add_argument("--model", default="models/gemini-2.5-flash")
    parser.add_argument("--delay-seconds", type=float, default=10.0)
    parser.add_argument("--staging-root", type=Path, default=DEFAULT_STAGING_ROOT)
    parser.add_argument("--overwrite-staging", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        languages = resolve_languages(args.only, args.from_lang)
        report = audit_sources()
        units = sum(item["translation_units"] for item in report.values())
        print("Audit localizzazione documentale superato.")
        print(f"Sorgenti italiane: {len(DOCUMENT_FILES)} (guide 10, presentazioni 2, disclaimer 2)")
        print(f"Lingue selezionate: {len(languages)} ({', '.join(languages)})")
        print(f"Unità testuali per lingua: {units}")
        print(f"Output eventuali: {len(DOCUMENT_FILES) * len(languages)}")
        for filename, details in report.items():
            print(f"- {filename}: {details['translation_units']} unità")
        if not args.execute:
            print("Modalità audit: nessuna API chiamata e nessun file scritto.")
            return 0
        execute_translation(
            languages, args.staging_root, args.model, args.delay_seconds,
            args.overwrite_staging,
        )
        return 0
    except Exception as error:
        print(f"ERRORE: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
