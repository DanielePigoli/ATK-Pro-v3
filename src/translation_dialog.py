import logging
import os
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QComboBox, QTextEdit, QFileDialog, QSplitter, QWidget, QProgressBar, QMessageBox, QLineEdit
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

from translation_processor import TranslationWorker

try:
    from key_manager import (
        missing_provider_credentials_message,
        normalize_provider_name,
        provider_requires_credentials,
    )
except ImportError:
    from src.key_manager import (
        missing_provider_credentials_message,
        normalize_provider_name,
        provider_requires_credentials,
    )

TARGET_LANGUAGES = [
    "Italiano", "English", "Español", "Français", "Deutsch", "Português",
    "Русский", "العربية", "Nederlands", "עברית", "日本語", "中文",
    "Polski", "Türkçe", "Dansk", "Norsk", "Tiếng Việt", "Ελληνικά",
    "Română", "Svenska",
]

TARGET_LANGUAGE_BY_INTERFACE = {
    "it": "Italiano",
    "en": "English",
    "es": "Español",
    "fr": "Français",
    "de": "Deutsch",
    "pt": "Português",
    "ru": "Русский",
    "ar": "العربية",
    "nl": "Nederlands",
    "he": "עברית",
    "ja": "日本語",
    "zh": "中文",
    "pl": "Polski",
    "tr": "Türkçe",
    "da": "Dansk",
    "no": "Norsk",
    "vi": "Tiếng Việt",
    "el": "Ελληνικά",
    "ro": "Română",
    "sv": "Svenska",
}

def get_msg(glossario, chiave, lingua):
    try:
        from main_gui_qt import get_msg as _get_msg
        res = _get_msg(glossario, chiave, lingua)
        return res if res is not None else chiave
    except:
        return chiave

class TranslationDialog(QDialog):
    def __init__(self, parent, glossario_data, lingua_corrente):
        super().__init__(parent)
        self.glossario = glossario_data
        self.glossario_data = glossario_data
        self.lingua = lingua_corrente
        self.setWindowTitle(self.gm("Traduzione Paleografica Assistita (LLM)"))
        self.setMinimumSize(900, 600)
        self.setWindowFlags(self.windowFlags() | Qt.WindowMinimizeButtonHint | Qt.WindowMaximizeButtonHint)
        self.setup_ui()
        try:
            self.load_settings()
        except Exception as e:
            logging.exception("[TranslationDialog] Errore in load_settings: %s", e)

    def gm(self, chiave):
        return get_msg(self.glossario, chiave, self.lingua)

    def setup_ui(self):
        self.setStyleSheet("""
            QDialog { background-color: #181818; color: #fff; border: 2px solid #a67c52; }
            QLabel { color: #fff; font-weight: bold; font-size: 13px; }
            QPushButton { background-color: #222; border: 1px solid #a67c52; padding: 6px 18px; border-radius: 6px; font-weight: bold; color: #fff; }
            QPushButton:hover { background-color: #333; }
            #btn_traduci { background-color: #a67c52; color: #fff; padding: 10px; font-size: 14px; border: none; }
            QTextEdit { background-color: #2a2a2a; color: #ccc; border: 1px solid #555; border-radius: 4px; font-size: 14px; padding: 5px; }
            QComboBox, QLineEdit { background-color: #2a2a2a; color: #fff; border: 1px solid #555; border-radius: 4px; padding: 4px; }
            QPushButton#btn_add_type { padding: 0px 0px 3px 0px; font-family: 'Segoe UI Symbol'; font-size: 13pt; color: #a67c52; }
            QPushButton#btn_edit_type { padding: 0px; font-family: 'Segoe UI Symbol'; font-size: 11pt; }
            QPushButton#btn_del_type { background-color: #2a1818; border-color: #8a3a3a; padding: 0px; font-family: 'Segoe UI Symbol'; font-size: 11pt; color: #cc6666; }
            QPushButton#btn_del_type:hover { background-color: #3a2020; }
        """)

        main_layout = QVBoxLayout(self)
        # --- Caveau chiavi (come GenealogyDialog) ---
        # RIMOSSO pulsante gestione caveau chiavi: già presente Cassaforte accanto all'API Key


        # --- Nuova disposizione: 3 righe orizzontali ---
        # Riga 1: Provider + Modello
        row1 = QHBoxLayout()
        lbl_prov = QLabel(self.gm("Provider IA:"))
        self.combo_prov = QComboBox()
        self.combo_prov.addItems([
            self.gm("Anthropic / Claude (Miglior Testo)"),
            self.gm("OpenAI (GPT-4o)"),
            self.gm("Google Gemini"),
            self.gm("DeepSeek (Economico/Testo)"),
            self.gm("Mistral"),
            self.gm("xAI / Grok"),
            self.gm("Groq (Veloce)"),
            self.gm("Hugging Face (Inference API)"),
            self.gm("Ollama (Locale/Privato)"),
        ])
        self.combo_prov.setMinimumWidth(180)
        self.combo_prov.setMaximumWidth(220)
        self.combo_prov.currentIndexChanged.connect(self._toggle_custom_model)
        self.lbl_custom_model = QLabel(self.gm("Modello:"))
        self.inp_custom_model = QLineEdit()
        self.inp_custom_model.setPlaceholderText(self.gm("Es. gpt-5-preview (lascia vuoto per default)"))
        self.inp_custom_model.setFixedWidth(110)
        row1.addWidget(lbl_prov)
        row1.addWidget(self.combo_prov)
        row1.addSpacing(10)
        row1.addWidget(self.lbl_custom_model)
        row1.addWidget(self.inp_custom_model)
        row1.addStretch()
        main_layout.addLayout(row1)

        # Riga 2: Tipologia + Azioni
        from document_type_manager import DocumentTypeManager
        self._dtm = DocumentTypeManager()
        row2 = QHBoxLayout()
        lbl_type = QLabel(self.gm("Tipologia Documento:"))
        lbl_type.setStyleSheet("font-weight: bold;")
        self.combo_type = QComboBox()
        self.combo_type.addItems(self._dtm.get_labels(service="translation"))
        self.combo_type.currentIndexChanged.connect(self._on_type_changed_tr)
        btn_add_type_tr = QPushButton("+")
        btn_add_type_tr.setObjectName("btn_add_type")
        btn_add_type_tr.setToolTip(self.gm("Aggiungi tipologia personalizzata"))
        btn_add_type_tr.setFixedSize(30, 30)
        btn_add_type_tr.clicked.connect(self._add_custom_type)
        self.btn_edit_type = QPushButton()
        self.btn_edit_type.setText("\u270f")
        self.btn_edit_type.setObjectName("btn_edit_type")
        self.btn_edit_type.setToolTip(self.gm("Modifica tipologia personalizzata selezionata"))
        self.btn_edit_type.setFixedSize(30, 30)
        self.btn_edit_type.clicked.connect(self._edit_custom_type)
        self.btn_edit_type.setVisible(False)
        self.btn_del_type = QPushButton()
        self.btn_del_type.setText("\u2715")
        self.btn_del_type.setObjectName("btn_del_type")
        self.btn_del_type.setToolTip(self.gm("Elimina tipologia personalizzata selezionata"))
        self.btn_del_type.setFixedSize(30, 30)
        self.btn_del_type.clicked.connect(self._delete_custom_type)
        self.btn_del_type.setVisible(False)
        row2.addWidget(lbl_type)
        row2.addWidget(self.combo_type)
        row2.addSpacing(8)
        row2.addWidget(btn_add_type_tr)
        row2.addWidget(self.btn_edit_type)
        row2.addWidget(self.btn_del_type)
        row2.addStretch()
        main_layout.addLayout(row2)

        # Riga 3: API + Cassaforte + Lingua
        row3 = QHBoxLayout()
        self.lbl_api = QLabel(self.gm("API Key:"))
        self.txt_api = QLineEdit()
        self.txt_api.setEchoMode(QLineEdit.Password)
        self.txt_api.setFixedWidth(200)
        btn_key_safe = QPushButton("🔑 " + self.gm("Cassaforte"))
        btn_key_safe.setStyleSheet("background-color: #2a2a2a; color: #f5f0e8; border: 1px solid #888; padding: 2px 10px; border-radius: 4px; font-size: 11px;")
        btn_key_safe.clicked.connect(self.open_key_manager)
        row3.addWidget(self.lbl_api)
        row3.addWidget(self.txt_api)
        row3.addWidget(btn_key_safe)
        row3.addSpacing(20)
        lbl_target = QLabel(self.gm("Lingua di Destinazione:"))
        self.combo_lingua = QComboBox()
        self.combo_lingua.addItems(TARGET_LANGUAGES)
        row3.addWidget(lbl_target)
        row3.addWidget(self.combo_lingua)
        row3.addStretch()
        main_layout.addLayout(row3)

        self._toggle_custom_model()

        # Splitter main content
        splitter = QSplitter(Qt.Horizontal)

        # --- LEFT PANE ---
        left_widget = QWidget()
        left_ly = QVBoxLayout(left_widget)
        left_ly.setContentsMargins(0, 10, 5, 0)

        # Origine
        header_orig = QHBoxLayout()
        lbl_orig = QLabel(self.gm("Testo Sorgente (Antico/Gregoriano/Dialetto):"))
        btn_load = QPushButton(self.gm("Carica File TXT"))
        btn_load.clicked.connect(self.carica_file)
        header_orig.addWidget(lbl_orig)
        header_orig.addStretch()
        header_orig.addWidget(btn_load)

        self.txt_orig = QTextEdit()
        self.txt_orig.setPlaceholderText(self.gm("Incolla qui la trascrizione cruda o carica un file .txt generato prima..."))

        # Contesto
        lbl_ctx = QLabel(self.gm("Glossario & Contesto (Opzionale, istruzioni alla IA):"))
        self.txt_ctx = QTextEdit()
        self.txt_ctx.setMaximumHeight(80)
        self.txt_ctx.setPlaceholderText(self.gm("Es. Traduci mantenendo arcaico. Cabella = dazio. Tassano = Nome proprio."))

        left_ly.addLayout(header_orig)
        left_ly.addWidget(self.txt_orig)
        left_ly.addWidget(lbl_ctx)
        left_ly.addWidget(self.txt_ctx)

        # --- RIGHT PANE ---
        right_widget = QWidget()
        right_ly = QVBoxLayout(right_widget)
        right_ly.setContentsMargins(5, 10, 0, 0)

        lbl_dest = QLabel(self.gm("Risultato Tradotto:"))
        self.txt_dest = QTextEdit()
        self.txt_dest.setPlaceholderText(self.gm("La traduzione moderna apparirà qui e potrà essere revisionata..."))

        # Export
        export_ly = QHBoxLayout()
        btn_save_txt = QPushButton(self.gm("Salva Traduzione (TXT)"))
        btn_save_txt.clicked.connect(lambda: self.esporta_risultato("txt"))
        btn_save_docx = QPushButton(self.gm("Esporta in Word (DOCX)"))
        btn_save_docx.clicked.connect(lambda: self.esporta_risultato("docx"))
        export_ly.addWidget(btn_save_txt)
        export_ly.addWidget(btn_save_docx)

        right_ly.addWidget(lbl_dest)
        right_ly.addWidget(self.txt_dest)
        right_ly.addLayout(export_ly)

        # Add to splitter
        splitter.addWidget(left_widget)
        splitter.addWidget(right_widget)

        # Give them 50/50 ratio
        splitter.setSizes([500, 500])
        main_layout.addWidget(splitter, 1) # stretch 1

        # Bottom Bar
        bottom_ly = QHBoxLayout()
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setRange(0, 0) # Indeterminate spinning

        self.btn_traduci = QPushButton("✨ " + self.gm("Traduci Testo ORA"))
        self.btn_traduci.setObjectName("btn_traduci")
        self.btn_traduci.clicked.connect(self.avvia_traduzione)

        bottom_ly.addWidget(self.progress_bar, 1)
        bottom_ly.addWidget(self.btn_traduci)

        main_layout.addLayout(bottom_ly)

    def open_key_manager_dialog(self):
        try:
            from key_manager import KeyManager
            km = KeyManager()
            km.open_manager_dialog(self)
        except Exception as e:
            QMessageBox.critical(
                self,
                self.gm("Errore"),
                self.gm("Impossibile aprire il gestore chiavi: {err}").format(err=e),
            )

    def _toggle_custom_model(self):
        prov = self.combo_prov.currentText()
        self.inp_custom_model.setPlaceholderText(self.gm("Es. gpt-5-preview (lascia vuoto per default)"))
        if "Gemini" in prov:
            self.lbl_api.setText(self.gm("Google Gemini API Key:"))
            self.lbl_custom_model.setVisible(False)
            self.inp_custom_model.setVisible(False)
            self.inp_custom_model.clear()
        elif "OpenAI" in prov:
            self.lbl_api.setText(self.gm("OpenAI API Key:"))
            self.lbl_custom_model.setVisible(True)
            self.inp_custom_model.setVisible(True)
        elif "DeepSeek" in prov:
            self.lbl_api.setText(self.gm("DeepSeek API Key:"))
            self.lbl_custom_model.setVisible(True)
            self.inp_custom_model.setVisible(True)
        elif "Mistral" in prov:
            self.lbl_api.setText(self.gm("Mistral API Key:"))
            self.lbl_custom_model.setVisible(True)
            self.inp_custom_model.setVisible(True)
        elif "xAI" in prov:
            self.lbl_api.setText(self.gm("xAI API Key:"))
            self.lbl_custom_model.setVisible(True)
            self.inp_custom_model.setVisible(True)
        elif "Groq" in prov:
            self.lbl_api.setText(self.gm("Groq API Key:"))
            self.lbl_custom_model.setVisible(True)
            self.inp_custom_model.setVisible(True)
        elif "Ollama" in prov:
            self.lbl_api.setText(self.gm("Host Ollama (es. http://localhost:11434):"))
            self.lbl_custom_model.setVisible(True)
            self.inp_custom_model.setVisible(True)
            self.inp_custom_model.setPlaceholderText(self.gm("Es. llava, llama3.2-vision, qwen2.5vl"))
            current_api = self.txt_api.text().strip()
            if current_api and not current_api.lower().startswith(("http://", "https://")):
                self.txt_api.clear()
            self.txt_api.setPlaceholderText("http://localhost:11434")
        elif "Hugging Face" in prov:
            self.lbl_api.setText(self.gm("Hugging Face Token (hf_...):"))
            self.lbl_custom_model.setVisible(True)
            self.inp_custom_model.setVisible(True)
            self.inp_custom_model.setPlaceholderText(self.gm("Es. Qwen/Qwen2.5-VL-7B-Instruct"))
        else:
            self.lbl_api.setText(self.gm("Anthropic API Key:"))
            self.lbl_custom_model.setVisible(True)
            self.inp_custom_model.setVisible(True)

    def _on_type_changed_tr(self):
        label = self.combo_type.currentText()
        is_custom = self._dtm.is_custom(label)
        self.btn_edit_type.setVisible(True)
        has_ov = not is_custom and self._dtm.has_builtin_override(label, "translation")
        self.btn_edit_type.setStyleSheet(
            "background-color: #2a2a1a; border: 1px solid #cc9922; color: #ffcc44;"
            if has_ov else ""
        )
        self.btn_edit_type.setToolTip(
            self.gm("Override prompt attivo — clicca per modificare") if has_ov
            else self.gm("Modifica prompt tipologia selezionata")
        )
        self.btn_del_type.setVisible(is_custom)

    def _add_custom_type(self):
        from new_doc_type_dialog import NewDocTypeDialog
        dlg = NewDocTypeDialog(self, lingua=self.lingua, glossario_data=self.glossario_data)
        if dlg.exec() and dlg.result_data:
            ok = self._dtm.add_custom_type(**dlg.result_data)
            if ok:
                label = self._dtm.CUSTOM_PREFIX + dlg.result_data["label"]
                self.combo_type.addItem(label)
                self.combo_type.setCurrentText(label)
            else:
                QMessageBox.warning(self, self.gm("Attenzione"), self.gm("Una tipologia con questo nome esiste già."))

    def _edit_custom_type(self):
        label = self.combo_type.currentText()
        if self._dtm.is_custom(label):
            data = self._dtm.get_custom_data(label)
            if not data:
                return
            from new_doc_type_dialog import NewDocTypeDialog
            dlg = NewDocTypeDialog(self, existing_data=data, lingua=self.lingua, glossario_data=self.glossario_data)
            if dlg.exec() and dlg.result_data:
                self._dtm.update_custom_type(**dlg.result_data)
        else:
            from prompt_edit_dialog import PromptEditDialog
            dlg = PromptEditDialog(self._dtm, label, "translation", parent=self,
                                   lingua=self.lingua, glossario_data=self.glossario_data)
            if dlg.exec():
                self._on_type_changed_tr()

    def _delete_custom_type(self):
        label = self.combo_type.currentText()
        msg = QMessageBox(self)
        msg.setWindowTitle(self.gm("Elimina Tipologia"))
        msg.setText(self.gm("Rimuovere '%s' dalla lista?") % label)
        btn_si = msg.addButton(self.gm("Si"), QMessageBox.ButtonRole.YesRole)
        msg.addButton(self.gm("No"), QMessageBox.ButtonRole.NoRole)
        msg.exec()
        if msg.clickedButton() == btn_si:
            self._dtm.delete_custom_type(label)
            idx = self.combo_type.findText(label)
            if idx >= 0:
                self.combo_type.removeItem(idx)

    def load_settings(self):
        try:
            from config_utils import _config_file_path
            import json, os
            cfg = _config_file_path()
            if os.path.exists(cfg):
                with open(cfg, 'r', encoding='utf-8') as f:
                    prefs = json.load(f)
                
                # API and Provider (Same as OCR)
                self.txt_api.setText(prefs.get('ocr_api_key', ''))
                prov = prefs.get('ocr_provider', 0)
                self.combo_prov.setCurrentIndex(prov)
                # Ripristina tipologia documentale
                saved_type = prefs.get('translation_doc_type', '')
                if saved_type:
                    idx = self.combo_type.findText(saved_type)
                    if idx >= 0: self.combo_type.setCurrentIndex(idx)
                # Translation specific
                self.txt_ctx.setText(prefs.get('translation_context', ''))
                self.inp_custom_model.setText(prefs.get('translation_custom_model', ''))

            # Pre-carica la prima chiave disponibile dalla Cassaforte, come avviene in OCR.
            try:
                from key_manager import KeyManager, preload_vault_key
                prov_str = normalize_provider_name(self.combo_prov.currentText())
                preloaded = preload_vault_key(prov_str, self.txt_api.text(), KeyManager())
                if preloaded != self.txt_api.text().strip():
                    self.txt_api.setText(preloaded)
                    logging.debug("[TranslationDialog] Chiave pre-caricata da Cassaforte (%s).", prov_str)
            except Exception as km_e:
                logging.warning("[TranslationDialog] Impossibile caricare chiave da Cassaforte: %s", km_e)
            
            # Default target language follows the current interface language when supported.
            default_autonym = TARGET_LANGUAGE_BY_INTERFACE.get(str(self.lingua).lower(), "English")
            idx = self.combo_lingua.findText(default_autonym)
            if idx >= 0:
                self.combo_lingua.setCurrentIndex(idx)
                    
        except Exception as e:
            logging.exception("[TranslationDialog] Errore caricamento impostazioni: %s", e)

    def save_settings(self):
        try:
            from config_utils import _write_config_prefs
            _write_config_prefs('ocr_api_key', self.txt_api.text().strip())
            _write_config_prefs('ocr_provider', self.combo_prov.currentIndex())
            _write_config_prefs('translation_doc_type', self.combo_type.currentText())
            _write_config_prefs('translation_context', self.txt_ctx.toPlainText().strip())
            _write_config_prefs('translation_custom_model', self.inp_custom_model.text().strip())
        except:
            pass

    def carica_file(self):
        path, _ = QFileDialog.getOpenFileName(
            self,
            self.gm("Seleziona file di testo"),
            "",
            self.gm("File di testo (*.txt);;Tutti i file (*.*)"),
        )
        if path:
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    self.txt_orig.setPlainText(f.read())
            except Exception as e:
                QMessageBox.warning(
                    self,
                    self.gm("Errore"),
                    self.gm("Impossibile leggere il file: {err}").format(err=e),
                )

    def avvia_traduzione(self):
        src_text = self.txt_orig.toPlainText().strip()
        if not src_text:
            QMessageBox.warning(self, self.gm("Attenzione"), self.gm("Immettere o caricare del testo sorgente prima di tradurre."))
            return

        api_key = self.txt_api.text().strip()
        prov_str = normalize_provider_name(self.combo_prov.currentText())
        # I provider locali non richiedono chiavi remote.
        if not api_key and provider_requires_credentials(prov_str):
            QMessageBox.warning(
                self,
                self.gm("Attenzione"),
                self.gm(missing_provider_credentials_message(prov_str)),
            )
            return

        self.save_settings()

        # Costruisce il prompt dalla tipologia documentale selezionata
        doc_type = self.combo_type.currentText()
        if self._dtm.is_custom(doc_type):
            custom_tr = self._dtm.get_translation_prompt(doc_type) or ""
            from translation_prompts import compose_translation_prompt
            final_prompt_text = compose_translation_prompt(
                doc_type="Documento Generico / Non Classificato",
                source_text=src_text,
                target_lang=self.combo_lingua.currentText(),
                context_info=(custom_tr + "\n" + self.txt_ctx.toPlainText().strip()).strip()
            )
        else:
            from translation_prompts import compose_translation_prompt
            final_prompt_text = compose_translation_prompt(
                doc_type=doc_type,
                source_text=src_text,
                target_lang=self.combo_lingua.currentText(),
                context_info=self.txt_ctx.toPlainText().strip()
            )

        self.btn_traduci.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.txt_dest.setPlainText(self.gm("Elaborazione della traduzione in corso. Potrebbe richiedere alcune decine di secondi..."))

        self.worker = TranslationWorker(
            provider=prov_str,
            api_key=api_key,
            source_text=final_prompt_text,  # il prompt già include il testo sorgente
            target_lang_autonym=self.combo_lingua.currentText(),
            context_info="",  # già incluso nel prompt composto
            custom_model=self.inp_custom_model.text().strip()
        )
        self.worker.finished.connect(self.on_traduzione_completata)
        self.worker.start()

    def on_traduzione_completata(self, success, text):
        self.btn_traduci.setEnabled(True)
        self.progress_bar.setVisible(False)
        
        if success:
            self.txt_dest.setPlainText(text)
        else:
            self.txt_dest.setPlainText("")
            QMessageBox.critical(self, self.gm("Errore API"), text)

    def esporta_risultato(self, format_ext):
        content = self.txt_dest.toPlainText().strip()
        if not content:
            QMessageBox.warning(self, self.gm("Attenzione"), self.gm("Non ci sono risultati da esportare."))
            return

        filter_str = self.gm("Documento testo (*.txt)") if format_ext == "txt" else self.gm("Microsoft Word (*.docx)")
        # Disabilito momentaneamente il DontUseNativeDialog che causa glitch stilistici sui Windows moderni, reintroduco il parent nullo per evitare i break e i crash alla memory release.
        filename, _ = QFileDialog.getSaveFileName(None, self.gm("Salva File"), f"Traduzione.{format_ext}", filter_str)
        if filename:
            try:
                if format_ext == "txt":
                    with open(filename, 'w', encoding='utf-8') as f:
                        f.write(content)
                elif format_ext == "docx":
                    import docx
                    doc = docx.Document()
                    doc.add_paragraph(content)
                    doc.save(filename)
                QMessageBox.information(self, self.gm("Successo"), self.gm("File salvato in:\n") + filename)
            except Exception as e:
                QMessageBox.critical(self, self.gm("Errore"), f"{self.gm('Impossibile salvare il file:')}\n{e}")

    def open_key_manager(self):
        from key_manager import KeyManager
        km = KeyManager()
        import platform, subprocess
        if os.path.exists(km.file_path):
            try:
                if platform.system() == 'Windows': os.startfile(km.file_path)
                elif platform.system() == 'Darwin': subprocess.run(['open', km.file_path])
                else: subprocess.run(['xdg-open', km.file_path])
            except: QMessageBox.warning(self, self.gm("Errore"), self.gm("Impossibile aprire il file CSV."))
        else:
            QMessageBox.warning(self, self.gm("Errore"), self.gm("File chiavi non trovato."))
