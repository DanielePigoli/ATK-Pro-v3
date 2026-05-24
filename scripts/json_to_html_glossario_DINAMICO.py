#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
json_to_html_glossario.py — generatore dinamico per ATK-Pro
Converte il glossario multilingue JSON in HTML tabellare con sezioni.

Input:  docs_generali/glossario_multilingua_ATK-Pro.json
Output: docs_generali/glossario_multilingua_ATK-Pro.html

Caratteristica principale:
- non usa un elenco hardcoded delle sezioni;
- genera automaticamente una tabella per ogni sezione del JSON che sia una lista di voci;
- ignora solo blocchi tecnici non tabellari, come metadata;
- mantiene eventuali nuove sezioni future senza dover modificare lo script.
"""

import html
import json
import os
import re
import sys
from datetime import datetime




def configure_stdout():
    """Rende l'output console compatibile anche con PowerShell/Windows cp1252."""
    try:
        if hasattr(sys.stdout, "reconfigure"):
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        if hasattr(sys.stderr, "reconfigure"):
            sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass


configure_stdout()

# Ordine preferito delle lingue note. Eventuali nuove colonne vengono aggiunte in coda.
LINGUE_PREFERITE = [
    "IT", "EN", "ES", "DE", "FR", "PT", "NL", "AR", "HE", "RU",
    "JA", "SV", "ZH", "RO", "EL", "PL", "DA", "NO", "TR", "VI"
]

LANG_EMOJIS = {
    "IT": "🇮🇹", "EN": "🇬🇧", "ES": "🇪🇸", "DE": "🇩🇪", "FR": "🇫🇷",
    "PT": "🇵🇹", "NL": "🇳🇱", "AR": "🇸🇦", "HE": "🇮🇱", "RU": "🇷🇺",
    "JA": "🇯🇵", "SV": "🇸🇪", "ZH": "🇨🇳", "RO": "🇷🇴", "EL": "🇬🇷",
    "PL": "🇵🇱", "DA": "🇩🇰", "NO": "🇳🇴", "TR": "🇹🇷", "VI": "🇻🇳"
}

# Solo etichette estetiche: non determina quali sezioni vengano incluse.
SECTION_LABELS = {
    "banner_sostegno": "📢 Banner di Sostegno",
    "funzioni_atkpro": "✨ Funzioni ATK-Pro",
    "etichette_gui": "🖥️ Etichette GUI",
    "etichette_menu": "Sezione: Etichette Menu",
    "menu_servizi": "🔧 Menu Servizi",
    "etichette_output": "📤 Etichette Output",
    "messaggi_dialogo": "💬 Messaggi Dialogo",
    "visualizzatore": "🖼️ Visualizzatore Immagini e Metadati",
    "prompt_ricerca_assistita": "🤖 Prompt Ricerca Assistita",
    "prompt_translation": "🌐 Prompt Traduzione",
    "prompt_gedcom": "🧬 Prompt GEDCOM",
}

# Chiavi tecniche da non trasformare in tabelle.
SEZIONI_DA_IGNORARE = {"metadata", "meta", "_metadata", "__metadata__"}


def current_project_version(project_root, metadata):
    """Legge la versione dall'app; usa metadata/fallback solo se la fonte non è disponibile."""
    sources = [
        (
            os.path.join(project_root, "src", "main_gui_qt.py"),
            r'^\s*VERSION\s*=\s*["\']([^"\']+)["\']',
        ),
        (
            os.path.join(project_root, "ATK-Pro-Installer.iss"),
            r'^\s*#define\s+MyAppVersion\s+["\']([^"\']+)["\']',
        ),
    ]
    for path, pattern in sources:
        if not os.path.exists(path):
            continue
        try:
            with open(path, "r", encoding="utf-8") as f:
                match = re.search(pattern, f.read(), re.MULTILINE)
            if match:
                return match.group(1).strip()
        except OSError:
            continue

    metadata_version = metadata.get("versione") if isinstance(metadata, dict) else None
    return str(metadata_version).strip() if metadata_version else "dev"


def escape(value):
    """Converte un valore qualunque in testo HTML sicuro."""
    if value is None:
        return ""
    return html.escape(str(value), quote=True)


def humanize_section_key(section_key):
    """Crea un titolo leggibile per sezioni nuove non presenti in SECTION_LABELS."""
    if section_key in SECTION_LABELS:
        return SECTION_LABELS[section_key]
    return "📁 " + section_key.replace("_", " ").strip().title()


def is_glossary_section(section_data):
    """Riconosce una sezione tabellare: lista non vuota di dizionari."""
    return (
        isinstance(section_data, list)
        and len(section_data) > 0
        and all(isinstance(entry, dict) for entry in section_data)
    )


def discover_sections(glossario):
    """Restituisce tutte le sezioni tabellari nell'ordine in cui compaiono nel JSON."""
    sections = []
    for section_key, section_data in glossario.items():
        if section_key in SEZIONI_DA_IGNORARE:
            continue
        if is_glossary_section(section_data):
            sections.append((section_key, section_data))
    return sections


def discover_columns(sections):
    """
    Determina le colonne da mostrare.
    'messaggio' resta sempre la prima; le lingue note seguono LINGUE_PREFERITE;
    eventuali nuove chiavi future vengono aggiunte in coda.
    """
    found_keys = set()
    for _, section_data in sections:
        for entry in section_data:
            found_keys.update(entry.keys())

    columns = ["messaggio"]
    columns.extend([lang for lang in LINGUE_PREFERITE if lang in found_keys])

    extra_keys = sorted(
        key for key in found_keys
        if key not in columns and key not in {"messaggio"}
    )
    columns.extend(extra_keys)
    return columns


def build_css():
    return """        /* Stili specifici per il glossario */
        header p {
            text-align: center !important;
            margin: 5px 0;
        }

        .glossario-container {
            max-width: 1400px;
            margin: 0 auto;
        }

        .glossario-header {
            text-align: center;
            margin-bottom: 20px;
        }

        .table-wrapper {
            width: 100%;
            overflow-x: auto;
            margin: 15px 0;
            border: 2px solid #a67c52;
            border-radius: 4px;
        }

        .metadata {
            background: rgba(230, 210, 165, 0.7) !important;
            border: 2px solid #a67c52 !important;
            border-radius: 8px;
            padding: 15px 30px !important;
            margin: 15px 0 !important;
            color: #4a2c1a !important;
        }

        .metadata strong {
            color: #2a1a0a !important;
        }

        table {
            width: 100%;
            border-collapse: collapse;
            margin: 15px 0;
            border: 2px solid #a67c52 !important;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif !important;
        }

        table th, table td {
            border: 1px solid #a67c52 !important;
            padding: 10px 6px;
            text-align: center;
            vertical-align: middle;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif !important;
            min-width: 120px;
            max-width: 320px;
            word-break: normal;
            overflow-wrap: anywhere;
            white-space: normal;
        }

        table th {
            background: rgba(230, 210, 165, 0.6) !important;
            font-weight: 700 !important;
            white-space: normal;
            word-break: break-word;
            color: #4a2c1a !important;
            border: 1px solid #a67c52 !important;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif !important;
            font-size: 0.95em !important;
            line-height: 1.4 !important;
        }

        table td {
            background: rgba(255, 255, 255, 0.3) !important;
        }

        .section-title {
            font-size: 1.3em;
            margin: 30px 0 15px 0;
            padding: 15px 20px;
            border: 2px solid #a67c52 !important;
            border-radius: 8px;
            background: rgba(230, 210, 165, 0.6) !important;
            font-weight: bold;
            color: #4a2c1a !important;
            display: inline-block;
            min-width: 100%;
            box-sizing: border-box;
        }

        .section {
            margin: 20px 0;
            padding: 0 30px;
        }

        /* Uniforma font size per AR e HE, se presenti */
        th[data-col="AR"], th[data-col="HE"],
        td[data-col="AR"], td[data-col="HE"] {
            font-size: 0.80em !important;
            line-height: 1.3 !important;
        }
"""


def column_header(column):
    if column == "messaggio":
        return "Messaggio"
    flag = LANG_EMOJIS.get(column, "")
    if flag:
        return f"{flag}<br>{escape(column)}"
    return escape(column)


def render_section(section_key, section_data, columns):
    section_label = humanize_section_key(section_key)
    html_parts = [f"""        <div class="section">
            <h2 class="section-title">{escape(section_label)}</h2>
            <div class="table-wrapper">
                <table class="glossario-table">
                    <thead>
                        <tr>
"""]

    for column in columns:
        html_parts.append(f'                            <th data-col="{escape(column)}">{column_header(column)}</th>\n')

    html_parts.append("""                        </tr>
                    </thead>
                    <tbody>
""")

    for entry in section_data:
        html_parts.append("                        <tr>\n")
        for column in columns:
            value = escape(entry.get(column, ""))
            if column == "messaggio":
                value = f"<strong>{value}</strong>"
            html_parts.append(f'                            <td data-col="{escape(column)}">{value}</td>\n')
        html_parts.append("                        </tr>\n")

    html_parts.append("""                    </tbody>
                </table>
            </div>
        </div>
""")
    return "".join(html_parts)


def json_to_html_glossario():
    """Carica JSON glossario e genera HTML tabellare con sezioni dinamiche."""

    # Percorsi relativi alla root del progetto: script collocato in /scripts.
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    json_path = os.path.join(project_root, "docs_generali", "glossario_multilingua_ATK-Pro.json")
    html_path = os.path.join(project_root, "docs_generali", "glossario_multilingua_ATK-Pro.html")

    if not os.path.exists(json_path):
        print(f"ERRORE: File non trovato: {json_path}")
        return False

    try:
        with open(json_path, "r", encoding="utf-8") as f:
            glossario = json.load(f)
    except json.JSONDecodeError as exc:
        print(f"ERRORE: JSON non valido: {exc}")
        return False

    if not isinstance(glossario, dict):
        print("ERRORE: Struttura non valida: la radice del JSON deve essere un oggetto/dizionario.")
        return False

    sections = discover_sections(glossario)
    if not sections:
        print("ERRORE: Nessuna sezione tabellare trovata nel JSON.")
        return False

    columns = discover_columns(sections)

    metadata = glossario.get("metadata", {}) if isinstance(glossario.get("metadata", {}), dict) else {}
    versione = current_project_version(project_root, metadata)
    timestamp = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    responsabile = metadata.get("responsabile", "Daniele Pigoli")

    html_content = f"""<!DOCTYPE html>
<html lang="it">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Glossario Multilingue ATK-Pro v{escape(versione)}</title>
    <link rel="stylesheet" href="../assets/common/testuali/atk_style.css">
    <style>
{build_css()}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🌍 Glossario Multilingue ATK-Pro</h1>
            <p><strong>Versione {escape(versione)}</strong> – {len(columns) - 1} colonne linguistiche/supporto</p>
            <p style="font-size: 0.95em; margin-top: 10px; color: #5a3e2b;">Antenati Toolkit Pro</p>
        </header>
        <div class="metadata">
            <strong>📅 Generato:</strong> {escape(timestamp)} |
            <strong>👤 Responsabile:</strong> {escape(responsabile)} |
            <strong>📚 Sezioni:</strong> {len(sections)}
        </div>
"""

    for section_key, section_data in sections:
        html_content += render_section(section_key, section_data, columns)

    html_content += """        <footer>
            <p><strong>Sezione: Documento ufficiale del progetto ATK‑Pro.</strong> Ogni voce è predisposta per integrazione in MUI/DLL o file .po/.mo. Il glossario va versionato e aggiornato a ogni nuova milestone linguistica.</p>
        </footer>
    </div>
</body>
</html>
"""

    os.makedirs(os.path.dirname(html_path), exist_ok=True)
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html_content)

    print(f"OK: Glossario HTML generato con {len(sections)} sezioni: {html_path}")
    return True


if __name__ == "__main__":
    success = json_to_html_glossario()
    exit(0 if success else 1)
