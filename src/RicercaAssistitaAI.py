# RicercaAssistitaAI.py
# Modulo per la ricerca genealogica assistita da AI in ATK-Pro
# Uniforme a ATK_Style e integrato con la logica multi-provider/chiavi

from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QComboBox, QTextEdit, QLineEdit, QFormLayout, QProgressBar, QMessageBox, QInputDialog, QCheckBox, QWidget, QVBoxLayout, QSizePolicy
from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import QIcon
import logging
import json
import os
import html
LOG_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'atkpro_debug.log'))
if not logging.getLogger('atkpro').hasHandlers():
    handler = logging.FileHandler(LOG_PATH, encoding='utf-8')
    handler.setFormatter(logging.Formatter('[%(asctime)s][%(levelname)s][%(name)s] %(message)s'))
    logging.getLogger('atkpro').addHandler(handler)
    logging.getLogger('atkpro').setLevel(logging.DEBUG)
logger = logging.getLogger('atkpro')
import os
from key_manager import (
    KeyManager,
    get_service_providers,
    missing_provider_credentials_message,
    normalize_provider_name,
    provider_requires_credentials,
    service_supports_provider,
)
from ai_utils import get_best_gemini_model
from multi_provider_handlers import get_handler


def _summarize_ai_result_payload(payload):
    try:
        data = json.loads(payload)
    except Exception:
        return "non-json"
    if isinstance(data, list):
        if data and isinstance(data[0], dict) and "results" in data[0]:
            total = sum(len(item.get("results") or []) for item in data if isinstance(item, dict))
            providers = [str(item.get("provider", "?")) for item in data if isinstance(item, dict)]
            return f"{total} righe da {len(providers)} provider ({', '.join(providers)})"
        return f"{len(data)} righe"
    return type(data).__name__


class RicercaAssistitaAIWorker(QThread):
    progress = Signal(int, str)
    finished = Signal(str)
    error = Signal(str)
    provider_changed = Signal(int, str, int)

    def __init__(self, query, provider, custom_model=None, show_all=False):
        super().__init__()
        self.query = query
        self.provider = normalize_provider_name(provider)
        self.custom_model = custom_model
        self.show_all = show_all
        self.km = KeyManager()
        self.current_key = None
        self.key_slot = 1
        self.key_count = 0

    def run(self):
        try:
            if not service_supports_provider("ai_search", self.provider):
                self.error.emit(f"Provider non supportato per Ricerca Assistita AI: {self.provider}")
                return
            logger.debug(
                "[AIWorker] Avvio ricerca: provider=%s, prompt_len=%s",
                self.provider,
                len(self.query or ""),
            )
            providers = [self.provider]
            # Fallback automatico: aggiungi altri provider con chiavi configurate
            all_providers = list(get_service_providers("ai_search"))
            for p in all_providers:
                if p not in providers and self.km.get_all_keys(p):
                    providers.append(p)
            all_results = [] if self.show_all else None
            for prov in providers:
                self.provider = prov # Aggiorna la variabile di classe con il provider correntemente elaborato
                keys = self.km.get_all_keys(prov)
                self.key_count = len(keys)
                if not keys:
                    continue
                provider_handled = False
                for attempt in range(len(keys)):
                    self.current_key = keys[self.km.current_indices.get(prov, 0)]
                    self.key_slot = self.km.current_indices.get(prov, 0) + 1
                    current_attempt = attempt + 1
                    max_attempts = len(keys)
                    self.provider_changed.emit(self.key_slot, prov, current_attempt)
                    try:
                        logger.debug(f"[AIWorker] Tentativo {current_attempt}/{max_attempts} con chiave slot {self.key_slot} (provider={prov})")
                        handler = get_handler(prov, self.current_key)
                        model = self.custom_model if self.custom_model else None
                        result_rows = handler.extract_genealogy(self.query, model=model)
                        result = json.dumps(result_rows, ensure_ascii=False, indent=2)
                        if self.show_all:
                            if isinstance(result_rows, list) and result_rows:
                                all_results.append({
                                    "provider": prov,
                                    "slot": self.key_slot,
                                    "results": result_rows,
                                    "raw": result
                                })
                                provider_handled = True
                                break
                        else:
                            if isinstance(result_rows, list) and result_rows:
                                logger.info(f"[AIWorker] Ricerca completata con successo (provider={prov}, slot={self.key_slot})")
                                self.finished.emit(result)
                                return
                        logger.info(f"[AIWorker] Nessun risultato utile da {prov} (slot {self.key_slot}), provo provider successivo...")
                    except Exception as e:
                        logger.warning(f"[AIWorker] Errore con chiave slot {self.key_slot} (provider={prov}): {e}")
                        if self.show_all:
                            all_results.append({
                                "provider": prov,
                                "slot": self.key_slot,
                                "results": [],
                                "raw": f"[ERRORE]: {e}"
                            })
                            provider_handled = True
                        self.km.get_next_key(prov, self.current_key)
                        if attempt == len(keys) - 1:
                            logger.error(f"[AIWorker] Tutte le chiavi per {prov} sono esaurite o non valide! Errore: {e}")
                            if prov == providers[-1] and not self.show_all:
                                self.error.emit(f"Tutte le chiavi per {prov} sono esaurite o non valide! Errore: {e}")
                                return
                if self.show_all and not provider_handled:
                    all_results.append({
                        "provider": prov,
                        "slot": None,
                        "results": [],
                        "raw": "[NESSUNA RISPOSTA]"
                    })
            if self.show_all and all_results:
                self.finished.emit(json.dumps(all_results, ensure_ascii=False, indent=2))
            else:
                self.finished.emit(json.dumps([], ensure_ascii=False))
        except Exception as e:
            logger.error(f"[AIWorker] Errore fatale: {e}")
            self.error.emit(str(e))

class RicercaAssistitaAIDialog(QDialog):
    def gm(self, chiave):
        try:
            from main_gui_qt import get_msg as _get_msg
        except Exception:
            try:
                from src.main_gui_qt import get_msg as _get_msg
            except Exception:
                return chiave
        res = _get_msg(self.glossario, chiave, self.lingua)
        return res if res else chiave

    def _update_key_status(self, slot, provider, key_count=None, error=False):
        """Aggiorna la label di stato chiave/provider e la progress bar."""
        stato = self.gm("Errore") if error else self.gm("Elaborazione...")
        testo = ""
        if slot and provider:
            testo = f"{self.gm('Provider')}: <b>{provider}</b> | {self.gm('Slot chiave')}: <b>{slot}</b>"
            if key_count is not None:
                testo += f" | {self.gm('Tentativo')}: <b>{key_count}</b>"
        elif provider:
            testo = f"{self.gm('Provider')}: <b>{provider}</b>"
        self.lbl_key_status.setText(testo)
        # Aggiorna anche la progress bar (formato)
        if hasattr(self, 'progress_bar') and self.progress_bar:
            self.progress_bar.setFormat(f"{testo.replace('<b>','').replace('</b>','')} | {stato}")
            if error:
                self.progress_bar.setStyleSheet(self.progress_bar.styleSheet() + "QProgressBar { color: #b00; }")
            else:
                self.progress_bar.setStyleSheet(self.progress_bar.styleSheet().replace("color: #b00;", "color: #222;"))

    def __init__(self, parent=None, glossario=None, lingua="it"):
        super().__init__(parent)
        self.glossario = glossario or {}
        self.lingua = lingua
        # --- Stili base widget ---
        inp_css = "background: #fff; color: #222; border: 1px solid #bbb; border-radius: 6px; padding: 2px 8px; font-size: 14px;"
        btn_css = "background: #e6e6e6; color: #222; border: 1px solid #bbb; border-radius: 6px; font-weight: bold;"
        lbl_css = "color: #333; font-weight: bold; font-size: 13px;"
        layout = QVBoxLayout(self)
        layout.setSpacing(6)
        layout.setContentsMargins(10, 10, 10, 10)

        # --- IMPOSTAZIONI FINESTRA (NATIVA) ---
        self.setWindowTitle(self.gm("Ricerca Assistita AI"))
        self.setWindowFlags(self.windowFlags() | Qt.WindowMinimizeButtonHint | Qt.WindowMaximizeButtonHint)

        # --- INTESTAZIONE: INPUT QUERY, PROVIDER, MODELLO, PROMPT, CHECKBOX ---
        form_top = QFormLayout()
        form_top.setSpacing(4)
        
        lbl_style = lbl_css + "min-height: 24px; color: #fff;"
        
        # Query
        self.inp_query = QTextEdit()
        self.inp_query.setPlaceholderText(self.gm("Soggetto, Luogo, Periodo, Fonti, ..."))
        self.inp_query.setStyleSheet(inp_css + "font-weight: bold; background: #f9f9e3; padding: 2px 6px; font-size: 13px;")
        self.inp_query.setMinimumHeight(44)
        self.inp_query.setMaximumHeight(44)
        
        lbl_query = QLabel(self.gm("Query di ricerca:"))
        lbl_query.setStyleSheet(lbl_style)
        lbl_query.setMinimumHeight(24)
        
        # Layout verticale per query ed esempio sotto
        query_layout = QVBoxLayout()
        query_layout.setContentsMargins(0, 0, 0, 0)
        query_layout.setSpacing(2)
        query_layout.addWidget(self.inp_query)
        
        lbl_hint = QLabel(self.gm("Esempio: Rossi, Bianchi a Firenze e Prato 1850-1900, battesimi e matrimoni"))
        lbl_hint.setStyleSheet("color: #ccc; font-size: 11px; font-style: italic; min-height: 14px;")
        query_layout.addWidget(lbl_hint)
        
        form_top.addRow(lbl_query, query_layout)
        
        # Provider
        self.combo_provider = QComboBox()
        self.combo_provider.setStyleSheet(inp_css)
        self.combo_provider.setMinimumHeight(24)
        self.combo_provider.addItems(list(get_service_providers("ai_search")))
        lbl_prov = QLabel(self.gm("Provider AI:"))
        lbl_prov.setStyleSheet(lbl_style)
        lbl_prov.setMinimumHeight(24)
        form_top.addRow(lbl_prov, self.combo_provider)
        
        # Modello custom
        self.inp_custom_model = QLineEdit()
        self.inp_custom_model.setPlaceholderText(self.gm("Modello custom (opzionale)"))
        self.inp_custom_model.setStyleSheet(inp_css)
        self.inp_custom_model.setMinimumHeight(24)
        lbl_model = QLabel(self.gm("Modello AI (opzionale):"))
        lbl_model.setStyleSheet(lbl_style)
        lbl_model.setMinimumHeight(24)
        form_top.addRow(lbl_model, self.inp_custom_model)
        
        # Prompt standard (solo i 4 reali)
        self.combo_prompt = QComboBox()
        self.combo_prompt.setStyleSheet(inp_css)
        self.combo_prompt.setMinimumHeight(24)
        self.combo_prompt.addItems([
            self.gm("Ricerca generale dettagliata"),
            self.gm("Strategie internazionali dettagliate"),
            self.gm("Ricerca atti specifici dettagliata"),
            self.gm("Ricerca avanzata con filtri")
        ])
        lbl_prompt = QLabel(self.gm("Prompt standard:"))
        lbl_prompt.setStyleSheet(lbl_style)
        lbl_prompt.setMinimumHeight(24)
        form_top.addRow(lbl_prompt, self.combo_prompt)
        
        # Checkbox tutti i provider (spuntata di default)
        self.chk_all_providers = QCheckBox(self.gm("Elabora con tutti i provider disponibili (multi-provider)"))
        self.chk_all_providers.setStyleSheet(lbl_css + "font-size: 12px; color: #e6c891; font-weight: bold; min-height: 20px;")
        self.chk_all_providers.setChecked(True)
        form_top.addRow(QLabel(), self.chk_all_providers)
        
        # Label stato chiave/provider
        self.lbl_key_status = QLabel()
        self.lbl_key_status.setStyleSheet("color:#e6c891;font-weight:bold;font-size:13px;padding:2px 0 2px 0;")
        self.lbl_key_status.setMinimumHeight(24)
        lbl_status = QLabel(self.gm("Stato provider/chiave:"))
        lbl_status.setStyleSheet(lbl_style + "color:#e6c891;")
        lbl_status.setMinimumHeight(24)
        form_top.addRow(lbl_status, self.lbl_key_status)
        layout.addLayout(form_top)

        # --- NOTE E PULSANTI NOTE ---
        form_note = QFormLayout()
        form_note.setSpacing(4)
        
        self.combo_note = QComboBox()
        self.combo_note.setStyleSheet(inp_css)
        self.combo_note.setMinimumWidth(260)
        self.combo_note.setMinimumHeight(24)
        lbl_sel_nota = QLabel(self.gm("Seleziona nota:"))
        lbl_sel_nota.setStyleSheet(lbl_style)
        form_note.addRow(lbl_sel_nota, self.combo_note)
        
        self.inp_note = QTextEdit()
        self.inp_note.setStyleSheet(inp_css + "min-height: 50px; font-size: 13px; min-width: 320px;")
        self.inp_note.setMinimumHeight(50)
        self.inp_note.setMinimumWidth(320)
        self.inp_note.setPlaceholderText(self.gm("Aggiungi o modifica una nota personale (opzionale)..."))
        lbl_cont_nota = QLabel(self.gm("Contenuto nota:"))
        lbl_cont_nota.setStyleSheet(lbl_style)
        form_note.addRow(lbl_cont_nota, self.inp_note)
        
        # Pulsanti note
        self.btn_save_note = QPushButton(self.gm("Salva nota"))
        self.btn_save_note.setStyleSheet(btn_css)
        self.btn_delete_note = QPushButton(self.gm("Elimina nota"))
        self.btn_delete_note.setStyleSheet(btn_css)
        self.btn_new_note = QPushButton(self.gm("Nuova nota"))
        self.btn_new_note.setStyleSheet(btn_css)
        
        btns_note_h = QHBoxLayout()
        btns_note_h.setSpacing(6)
        btns_note_h.setContentsMargins(0, 0, 0, 0)
        for btn in [self.btn_save_note, self.btn_delete_note, self.btn_new_note]:
            btn.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
            btn.setMinimumWidth(90)
            btn.setMaximumWidth(110)
            btn.setMinimumHeight(28)
            btn.setMaximumHeight(32)
            btn.setStyleSheet(btn_css + "font-size: 12px; padding: 4px 8px;")
            btns_note_h.addWidget(btn)
            
        btns_note_widget = QWidget()
        btns_note_widget.setLayout(btns_note_h)
        btns_note_widget.setMinimumHeight(32)
        btns_note_widget.setStyleSheet("margin-bottom: 2px;")
        lbl_azioni_nota = QLabel(self.gm("Azioni nota:"))
        lbl_azioni_nota.setStyleSheet(lbl_style)
        form_note.addRow(lbl_azioni_nota, btns_note_widget)
        
        layout.addLayout(form_note)

        # --- PULSANTE AVVIO ---
        self.btn_run = QPushButton(self.gm("SUGGERISCI PORTALI E QUERY"))
        self.btn_run.setStyleSheet(btn_css + "background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #e6c891, stop:1 #fffbe8); color: #222; font-size: 15px; border: 2px solid #a67c52; padding: 4px 0; margin-top: 6px;")
        self.btn_run.setMinimumHeight(36)
        self.btn_run.setMaximumWidth(420)
        layout.addWidget(self.btn_run, alignment=Qt.AlignHCenter)
        self.setMinimumSize(820, 600)
        self.resize(1100, 800)  # Apertura iniziale ampia
        self.setStyleSheet("""
            QDialog { background-color: #181818; color: #fff; border: 2px solid #a67c52; }
            QLabel { color: #fff; }
            QScrollBar:vertical {
                background: transparent;
                width: 2px;
                margin: 0px;
                border: none;
            }
            QScrollBar::handle:vertical {
                background-color: #a67c52;
                min-height: 20px;
                border-radius: 1px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #cfb58b;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                background: none;
                height: 0px;
            }
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                background: none;
            }
        """)
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setStyleSheet('''
            QProgressBar {
                border: 2.5px solid #e6c891;
                border-radius: 6px;
                text-align: center;
                font-weight: bold;
                font-size: 16px;
                color: #222;
                background-color: #fffbe8;
                min-height: 32px;
                margin-top: 6px;
                margin-bottom: 18px;
                padding: 6px 14px;
                letter-spacing: 0.5px;
            }
            QProgressBar::chunk {
                background-color: #e6c891;
                color: #222;
                border-radius: 6px;
                margin: 1px;
            }
        ''')
        self.progress_bar.setMinimumWidth(340)
        layout.addWidget(self.progress_bar)
        # Raggruppamento risultati
        self.lbl_group_by = QLabel(self.gm("Raggruppa risultati per:"))
        self.lbl_group_by.setStyleSheet(lbl_css)
        self.combo_group_by = QComboBox()
        self.combo_group_by.setStyleSheet(inp_css)
        self.combo_group_by.setMinimumWidth(200)
        self.combo_group_by.setMinimumHeight(30)
        for label, value in [
            ("(Nessuna aggregazione)", "(Nessuna aggregazione)"),
            ("Portale", "Portale"),
            ("Motivazione", "Motivazione"),
            ("Query di esempio", "Query di esempio"),
            ("Periodo", "Periodo"),
            ("Tipo atti", "Tipo atti"),
            ("Filtri/Strategie", "Filtri/Strategie"),
        ]:
            self.combo_group_by.addItem(self.gm(label), value)
        group_layout = QHBoxLayout()
        group_layout.addWidget(self.lbl_group_by)
        group_layout.addWidget(self.combo_group_by)
        group_widget = QWidget(); group_widget.setLayout(group_layout)
        layout.addWidget(group_widget)
        # Risultato
        self.txt_result = QTextEdit()
        self.txt_result.setReadOnly(True)
        self.txt_result.setStyleSheet("background-color: #1f1f1f; color: #ffffff; border: 1.5px solid #a67c52; border-radius: 6px; padding: 8px; font-size: 14px; min-height: 120px; min-width: 320px;")
        self.txt_result.setMinimumHeight(120)
        self.txt_result.setLineWrapMode(QTextEdit.WidgetWidth)
        layout.addWidget(self.txt_result, stretch=2)
        # Aggiorna anteprima raggruppamento quando cambia la selezione
        self.combo_group_by.currentIndexChanged.connect(self._update_grouped_preview)
        # Pulsante Salva Risultato (Markdown)
        self.btn_save_result = QPushButton(self.gm("SALVA RISULTATI AI"))
        self.btn_save_result.setStyleSheet(btn_css + "background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #a67c52, stop:1 #cfb58b); color: #fff; font-size: 15px; border: 2px solid #3a1f00; padding: 6px 0; margin-top: 6px;")
        self.btn_save_result.setMinimumHeight(44)
        self.btn_save_result.setEnabled(False)
        layout.addWidget(self.btn_save_result)
        # Pulsante Salva Risultato (HTML)
        self.btn_save_html = QPushButton(self.gm("SALVA RISULTATO HTML"))
        self.btn_save_html.setStyleSheet(btn_css + "background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #cfb58b, stop:1 #a67c52); color: #fff; font-size: 15px; border: 2px solid #3a1f00; padding: 6px 0; margin-top: 6px;")
        self.btn_save_html.setMinimumHeight(44)
        self.btn_save_html.setEnabled(False)
        layout.addWidget(self.btn_save_html)
        # Caveau chiavi
        layout.addSpacing(6)
        self.btn_manage_keys = QPushButton("🗝️ " + self.gm("GESTISCI CAVEAU CHIAVI (CSV)"))
        self.btn_manage_keys.setStyleSheet(btn_css)
        layout.addWidget(self.btn_manage_keys, alignment=Qt.AlignBottom)
        logger.debug("[RicercaAssistitaAIDialog] __init__ FINE")
        # --- Connessioni ---
        self.btn_run.clicked.connect(self.start_ai_search)
        self.combo_note.currentIndexChanged.connect(self._on_note_selected)
        self.btn_save_note.clicked.connect(self._on_save_note)
        self.btn_delete_note.clicked.connect(self._on_delete_note)
        self.btn_new_note.clicked.connect(self._on_new_note)
        self.btn_save_result.clicked.connect(self._on_save_result)
        self.btn_save_html.clicked.connect(self._on_save_result_html)
        self.btn_manage_keys.clicked.connect(self.open_key_manager)
        # --- Inizializzazione variabili note e risultati ---
        self.notes_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'ai_search_notes.json'))
        self.notes = self._load_notes()
        self._refresh_notes_combo()
        self._last_result_data = "[]"

    def _toggle_max_restore(self):
        """Alterna massimizza/ripristina per la finestra dialog."""
        if self.isMaximized():
            self.showNormal()
        else:
            self.showMaximized()

    def _on_save_result(self):
        from PySide6.QtWidgets import QFileDialog
        # Proponi come default la cartella delle note
        default_dir = os.path.dirname(self.notes_path)
        default_name = "risultato_ai.md"
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            self.gm("Salva risultato AI"),
            os.path.join(default_dir, default_name),
            f"{self.gm('File Markdown')} (*.md);;{self.gm('File di testo')} (*.txt);;{self.gm('Tutti i file')} (*)"
        )
        if file_path:
            if not file_path.lower().endswith((".md", ".txt")):
                file_path += ".md"
            try:
                # Usa il markdown raggruppato come in anteprima
                md = self._get_grouped_markdown()
                if file_path.lower().endswith('.md'):
                    with open(file_path, "w", encoding="utf-8") as f:
                        f.write(md)
                else:
                    # Rimuovi tag HTML per versione txt
                    import re
                    txt = re.sub(r'<[^>]+>', '', md.replace('<br>', '\n'))
                    with open(file_path, "w", encoding="utf-8") as f:
                        f.write(txt)
                QMessageBox.information(
                    self,
                    self.gm("Salvataggio riuscito"),
                    self.gm("Risultato AI salvato in:\n{file_path}").format(file_path=file_path),
                )
            except Exception as e:
                QMessageBox.critical(self, self.gm("Errore salvataggio"), str(e))

    def _on_save_result_html(self):
        from PySide6.QtWidgets import QFileDialog
        default_dir = os.path.dirname(self.notes_path)
        default_name = "risultato_ai.html"
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            self.gm("Salva risultato AI in HTML"),
            os.path.join(default_dir, default_name),
            f"{self.gm('File HTML')} (*.html);;{self.gm('Tutti i file')} (*)"
        )
        if not file_path:
            return
        if not file_path.lower().endswith((".html", ".htm")):
            file_path += ".html"
        try:
            result_html = self._get_grouped_markdown()
            html_content = self._render_result_html(result_html)
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(html_content)
            QMessageBox.information(
                self,
                self.gm("Salvataggio HTML riuscito"),
                self.gm("Risultato HTML salvato in:\n{file_path}").format(file_path=file_path),
            )
        except Exception as e:
            QMessageBox.critical(self, self.gm("Errore salvataggio HTML"), str(e))

    def _render_result_html(self, result_html):
        title = html.escape(self.gm("Risultati Ricerca Assistita AI"), quote=True)
        lang = html.escape(str(self.lingua).lower(), quote=True)
        return f"""<!DOCTYPE html>
<html lang="{lang}">
<head>
<meta charset="utf-8">
<title>{title}</title>
<style>
body {{
    background-color: #121212;
    color: #e0e0e0;
    font-family: 'Segoe UI', Arial, sans-serif;
    padding: 20px;
    margin: 0;
}}
.container {{
    max-width: 1200px;
    margin: 0 auto;
}}
h1, h2, h3, h4 {{
    color: #e6c891;
}}
</style>
</head>
<body>
<div class="container">
    <h1>{title}</h1>
    {result_html}
</div>
</body>
</html>"""

    def _map_raw_row_to_headers(self, row):
        mapping = {
            "Portale": ["Portale", "1", "portale", "PORTALE", "Nome"],
            "Motivazione": ["Motivazione", "2", "motivazione", "MOTIVAZIONE"],
            "Query di esempio": ["Query di esempio", "3", "query di esempio", "QUERY DI ESEMPIO", "Query"],
            "Periodo": ["Periodo", "4", "periodo", "PERIODO"],
            "Tipo atti": ["Tipo atti", "5", "tipo atti", "TIPO ATTI"],
            "Filtri/Strategie": ["Filtri/Strategie", "6", "filtri/strategie", "FILTRI/STRATEGIE"]
        }
        mapped = {}
        
        for header, possible_keys in mapping.items():
            val = None
            for pk in possible_keys:
                if pk in row:
                    val = row[pk]
                    break
            if val is not None:
                mapped[header] = val
            else:
                keys_list = list(mapping.keys())
                if header in keys_list:
                    idx = keys_list.index(header)
                    sorted_digit_keys = sorted([k for k in row.keys() if k.isdigit()], key=int)
                    if idx < len(sorted_digit_keys):
                        mapped[header] = row[sorted_digit_keys[idx]]
                        
        for k, v in row.items():
            is_mapped = False
            for header, possible_keys in mapping.items():
                if k in possible_keys or k == header:
                    is_mapped = True
                    break
            if not is_mapped and not k.isdigit():
                mapped[k] = v
                
        return mapped

    def _format_html_table(self, columns, rows):
        width_map = {
            "Portale": "18%",
            "Motivazione": "32%",
            "Query di esempio": "18%",
            "Periodo": "10%",
            "Tipo atti": "12%",
            "Filtri/Strategie": "15%",
            "Provider": "10%",
            "Slot": "5%"
        }
        
        th_html = ""
        for col in columns:
            w = width_map.get(col, "15%")
            col_safe = html.escape(self.gm(str(col)), quote=True)
            th_html += f'<th style="width: {w}; border: 1px solid #a67c52; background-color: #2b2b2b; color: #e6c891; padding: 8px; text-align: left; font-size: 13px;">{col_safe}</th>'
            
        tr_html = ""
        for row in rows:
            tr_html += '  <tr style="background-color: #222222; color: #ffffff;">\n'
            for col in columns:
                val = html.escape(str(row.get(col, '')), quote=True)
                import re
                val_formatted = re.sub(r'`(.*?)`', r'<code style="background-color: #333333; color: #e6c891; padding: 2px 4px; border-radius: 4px;">\1</code>', val)
                val_formatted = re.sub(r'\*\*(.*?)\*\*', r'<strong style="color: #e6c891;">\1</strong>', val_formatted)
                val_formatted = val_formatted.replace('\n', '<br>')
                tr_html += f'    <td style="border: 1px solid #a67c52; padding: 8px; text-align: left; font-size: 13px; vertical-align: top; word-wrap: break-word; color: #ffffff;">{val_formatted}</td>\n'
            tr_html += '  </tr>\n'
            
        table_html = f'''<table style="width: 100%; border-collapse: collapse; table-layout: fixed; font-family: 'Segoe UI', Arial, sans-serif; margin-top: 8px; margin-bottom: 16px;">
  <thead>
    <tr style="height: 32px;">
      {th_html}
    </tr>
  </thead>
  <tbody>
{tr_html}  </tbody>
</table>'''
        return table_html

    def _get_grouped_markdown(self):
        """Restituisce la tabella HTML premium raggruppata o piatta per salvataggio e anteprima."""
        try:
            data = json.loads(self._last_result_data)
            
            # Normalizzazione robusta dei dati: supportiamo sia il formato show_all = True (lista di provider)
            # sia il formato show_all = False (lista diretta di righe dei risultati).
            normalized_data = []
            if isinstance(data, list):
                if len(data) > 0 and isinstance(data[0], dict) and "provider" in data[0] and "results" in data[0]:
                    normalized_data = data
                else:
                    # È una lista diretta di righe di risultati. La inseriamo in una struttura provider fittizia.
                    normalized_data = [{
                        "provider": self.combo_provider.currentText(),
                        "slot": 1,
                        "results": data
                    }]
            else:
                normalized_data = []

            field = self.combo_group_by.currentData() or self.combo_group_by.currentText()
            
            if field == "(Nessuna aggregazione)":
                columns = ["Portale", "Motivazione", "Query di esempio", "Periodo", "Tipo atti", "Provider", "Slot"]
                flat_rows = []
                for prov_result in normalized_data:
                    prov = prov_result.get('provider', '?')
                    slot = prov_result.get('slot', '?')
                    rows = prov_result.get('results', [])
                    for row in rows:
                        mapped_row = self._map_raw_row_to_headers(row)
                        mapped_row["Provider"] = prov
                        mapped_row["Slot"] = str(slot)
                        flat_rows.append(mapped_row)
                
                custom_cols = set()
                for r in flat_rows:
                    custom_cols.update([k for k in r.keys() if k not in columns])
                final_cols = ["Portale", "Motivazione", "Query di esempio", "Periodo", "Tipo atti"] + sorted(list(custom_cols)) + ["Provider", "Slot"]
                
                return self._format_html_table(final_cols, flat_rows)

            grouped = {}
            for prov_result in normalized_data:
                prov = prov_result.get('provider', '?')
                slot = prov_result.get('slot', '?')
                rows = prov_result.get('results', [])
                for row in rows:
                    mapped_row = self._map_raw_row_to_headers(row)
                    key = mapped_row.get(field, None)
                    if not key:
                        key = mapped_row.get("Portale", self.gm("Sconosciuto"))
                    
                    import re
                    clean_key = re.sub(r'\*+', '', str(key)).strip()
                    if not clean_key:
                        clean_key = self.gm("Sconosciuto")
                        
                    if clean_key not in grouped:
                        grouped[clean_key] = []
                    
                    row_copy = mapped_row.copy()
                    if field in row_copy:
                        del row_copy[field]
                        
                    grouped[clean_key].append({
                        "row": row_copy,
                        "provider": prov,
                        "slot": str(slot)
                    })
            
            md = ""
            for clean_key, rows_in_group in grouped.items():
                field_safe = html.escape(self.gm(str(field)), quote=True)
                key_safe = html.escape(str(clean_key), quote=True)
                md += f'<h3 style="font-family: \'Segoe UI\', Arial, sans-serif; color: #a67c52; margin-top: 16px; margin-bottom: 8px;">{field_safe}: {key_safe}</h3>\n'
                
                columns_in_group = set()
                for r_data in rows_in_group:
                    columns_in_group.update(r_data["row"].keys())
                
                standard_order = ["Portale", "Motivazione", "Query di esempio", "Periodo", "Tipo atti", "Filtri/Strategie"]
                sorted_cols = [c for c in standard_order if c in columns_in_group and c != field]
                other_cols = sorted([c for c in columns_in_group if c not in standard_order and c != field])
                final_cols = sorted_cols + other_cols + ["Provider", "Slot"]
                
                flat_rows_in_group = []
                for r_data in rows_in_group:
                    r_copy = r_data["row"].copy()
                    r_copy["Provider"] = r_data["provider"]
                    r_copy["Slot"] = r_data["slot"]
                    flat_rows_in_group.append(r_copy)
                    
                md += self._format_html_table(final_cols, flat_rows_in_group) + "\n"
                
            return md
        except Exception as e:
            err = html.escape(str(e), quote=True)
            raw = html.escape(str(self._last_result_data), quote=True)
            error_label = html.escape(self.gm("Errore nel raggruppamento dati"), quote=True)
            return f"<p>{error_label}: {err}</p><pre>{raw}</pre>"

    def open_key_manager(self):
        try:
            from key_manager import KeyManager
            km = KeyManager()
            if not os.path.exists(km.file_path):
                # Crea un file vuoto se non esiste
                with open(km.file_path, "w", encoding="utf-8") as f:
                    pass
            os.startfile(km.file_path)
        except Exception as e:
            QMessageBox.critical(
                self,
                self.gm("Errore"),
                self.gm("Impossibile aprire il file delle chiavi: {err}").format(err=e),
            )

    def _load_notes(self):
        try:
            with open(self.notes_path, "r", encoding="utf-8") as f:
                notes = json.load(f)
            return notes if isinstance(notes, dict) else {}
        except Exception:
            return {}

    def _on_save_note(self):
        # Salva la nota corrente nel dizionario delle note e aggiorna la lista
        idx = self.combo_note.currentIndex()
        key = self.combo_note.itemText(idx)
        note_text = self.inp_note.toPlainText().strip()
        if key and idx > 0:
            self.notes[key] = note_text
        elif idx == 0 and note_text:
            # Se la nota è nuova, chiedi un nome
            from PySide6.QtWidgets import QInputDialog
            new_key, ok = QInputDialog.getText(self, self.gm("Nuova nota"), self.gm("Nome per la nota:"))
            if ok and new_key:
                self.notes[new_key] = note_text
                self._refresh_notes_combo()
                self.combo_note.setCurrentText(new_key)
        self._save_notes()

    def _save_notes(self):
        try:
            with open(self.notes_path, "w", encoding="utf-8") as f:
                json.dump(self.notes, f, indent=4, ensure_ascii=False)
        except Exception as e:
            logger.error(f"[RicercaAssistitaAIDialog] Errore salvataggio note: {e}")

    def _on_delete_note(self):
        idx = self.combo_note.currentIndex()
        if idx > 0:
            key = self.combo_note.itemText(idx)
            if key in self.notes:
                del self.notes[key]
                self._save_notes()
                self._refresh_notes_combo()
                self.combo_note.setCurrentIndex(0)

    def _refresh_notes_combo(self):
        self.combo_note.blockSignals(True)
        self.combo_note.clear()
        self.combo_note.addItem(self.gm("(Nessuna nota)"))
        for k in self.notes:
            self.combo_note.addItem(k)
        self.combo_note.blockSignals(False)
        self.inp_note.clear()

    def show_result(self, result):
        self.btn_run.setEnabled(True)
        self.progress_bar.setVisible(False)
        self.btn_save_result.setEnabled(True)
        self.btn_save_html.setEnabled(True)
        self._last_result_data = result  # Salva SEMPRE il risultato grezzo
        self._update_grouped_preview()

    def _update_grouped_preview(self):
        try:
            legend_title = html.escape(self.gm("Legenda risultati AI:"), quote=True)
            legend_items = [
                ("Provider", self.gm("Il servizio AI che ha generato la risposta (es. Claude, Gemini, ecc.)")),
                ("Slot", self.gm("La posizione della chiave usata nel caveau per quel provider")),
                ("Tabella", self.gm("Ogni colonna corrisponde a un'informazione richiesta dal prompt (es. Portale, Motivazione, Query di esempio, Periodo, Tipo atti)")),
            ]
            legend_items_html = "".join(
                "<li><b style='color: #e6c891;'>{label}</b>: {description}</li>".format(
                    label=html.escape(self.gm(label), quote=True),
                    description=html.escape(description, quote=True),
                )
                for label, description in legend_items
            )
            legenda = (
                "<div style=\"font-family: 'Segoe UI', Arial, sans-serif; color: #ffffff; margin-bottom: 12px;\">"
                f"<b style='color: #e6c891; font-size: 15px;'>{legend_title}</b><br>"
                "<ul style='margin-top: 4px; margin-bottom: 8px; padding-left: 20px; font-size: 13px; line-height: 1.4; color: #e0e0e0;'>"
                f"{legend_items_html}"
                "</ul>"
                "</div>"
            )
            md = self._get_grouped_markdown()
            self.txt_result.setHtml(legenda + md)
        except Exception as e:
            error_title = html.escape(self.gm("Errore caricamento anteprima"), quote=True)
            data_label = html.escape(self.gm("Dati"), quote=True)
            err = html.escape(str(e), quote=True)
            raw = html.escape(str(self._last_result_data), quote=True)
            self.txt_result.setHtml(f"<div style='color: #ff6b6b; font-family: \"Segoe UI\", sans-serif; font-size: 14px;'>{error_title}: {err}<br><br>{data_label}:<br>{raw}</div>")

    def show_error(self, e):
        self.btn_run.setEnabled(True)
        self.progress_bar.setVisible(False)
        title = self.gm("Errore AI")
        title_safe = html.escape(title, quote=True)
        err = html.escape(str(e), quote=True)
        self.txt_result.setHtml(f"<div style='color: #ff6b6b; font-family: \"Segoe UI\", sans-serif; font-size: 14px; font-weight: bold;'>{title_safe}: {err}</div>")
        self.txt_result.setFocus()
        QMessageBox.critical(self, title, str(e))

    def _on_note_selected(self, idx):
        # Seleziona la nota corrispondente e aggiorna il campo di testo
        key = self.combo_note.itemText(idx)
        if key in self.notes:
            self.inp_note.setPlainText(self.notes[key])
        else:
            self.inp_note.clear()

    def _on_new_note(self):
        # Crea una nuova nota vuota e chiede il nome
        from PySide6.QtWidgets import QInputDialog
        new_key, ok = QInputDialog.getText(self, self.gm("Nuova nota"), self.gm("Nome per la nuova nota:"))
        if ok and new_key:
            self.notes[new_key] = ""
            self._refresh_notes_combo()
            self.combo_note.setCurrentText(new_key)
            self.inp_note.clear()
            self._save_notes()
        else:
            self.combo_note.setCurrentIndex(0)

    def start_ai_search(self):
        from ai_search_prompts import get_prompt_base
        query = self.inp_query.toPlainText().strip()
        provider = normalize_provider_name(self.combo_provider.currentText())
        logger.info(
            "[RicercaAssistitaAIDialog] Avvio ricerca AI: provider=%s, query_len=%s",
            provider,
            len(query),
        )
        custom_model = self.inp_custom_model.text().strip() or None
        idx_prompt = self.combo_prompt.currentIndex()
        note_text = self.inp_note.toPlainText().strip() if self.combo_note.currentIndex() > 0 else ""
        if not query:
            QMessageBox.warning(self, self.gm("Attenzione"), self.gm("Inserisci una query di ricerca."))
            return
        show_all = self.chk_all_providers.isChecked()
        km = KeyManager()
        if not show_all and provider_requires_credentials(provider) and not km.has_keys(provider):
            QMessageBox.warning(
                self,
                self.gm("Attenzione"),
                self.gm(missing_provider_credentials_message(provider)),
            )
            return
        # Estrai luogo, periodo, tipo se presenti nella query (regex semplice)
        import re
        luogo = periodo = tipo = ""
        luogo_match = re.search(r"(?:a|in|presso|di|per)\s+([A-Z][a-zA-Z\s]+)", query)
        if luogo_match:
            luogo = luogo_match.group(1).strip()
        periodo_match = re.search(r"(\d{4}(?:-\d{4})?)", query)
        if periodo_match:
            periodo = periodo_match.group(1)
        tipo_match = re.search(r"(battesimi|matrimoni|morti|nascite|registri|atti|censimenti|parrocchiali|stato civile)", query, re.I)
        if tipo_match:
            tipo = tipo_match.group(1)
        # Componi il prompt base parametrico
        prompt_base = get_prompt_base(self.glossario, self.lingua, idx_prompt, query=query, luogo=luogo, periodo=periodo, tipo=tipo)
        # Componi prompt finale
        prompt_finale = prompt_base
        if note_text:
            prompt_finale += f"\n\nNOTA UTENTE:\n{note_text}"
        self.worker = RicercaAssistitaAIWorker(prompt_finale, provider, custom_model, show_all)
        logger.debug(f"[RicercaAssistitaAIDialog] Worker creato e avviato")
        self.progress_bar.setVisible(True)
        self.worker.progress.connect(lambda v, m: (self.progress_bar.setValue(v), self.progress_bar.setFormat(m)))
        self.worker.progress.connect(lambda v, m: logger.debug(f"[RicercaAssistitaAIDialog] Progresso: {v} - {m}"))
        self.worker.provider_changed.connect(self._update_key_status)
        self.worker.finished.connect(self.show_result)
        self.worker.error.connect(self.show_error)
        self.worker.finished.connect(lambda r: logger.info(
            "[RicercaAssistitaAIDialog] Ricerca completata: %s",
            _summarize_ai_result_payload(r),
        ))
        self.worker.error.connect(lambda e: logger.error(f"[RicercaAssistitaAIDialog] Errore: {e}"))
        self._update_key_status(0, provider, 1)
        self.worker.finished.connect(lambda _: self._update_key_status(self.worker.key_slot, self.worker.provider, self.worker.key_count, error=False))
        self.worker.error.connect(lambda _: self._update_key_status(self.worker.key_slot, self.worker.provider, self.worker.key_count, error=True))
        self.worker.start()
