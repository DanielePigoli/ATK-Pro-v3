import os
import json
import logging
import time
import re
import zipfile
import io
import xml.etree.ElementTree as ET
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QComboBox, QTextEdit, QFileDialog, 
                             QProgressBar, QMessageBox, QLineEdit, QFormLayout, QFrame, QWidget, QScrollArea, QInputDialog)
from PySide6.QtCore import Qt, QThread, Signal, QBuffer, QIODevice, QMutex, QWaitCondition
from PySide6.QtGui import QImage, QFont

try:
    import google.generativeai as genai
except ImportError:
    pass
from genealogy_prompts import compose_extraction_prompt
from gedcom_factory import GedcomGenerator
from key_manager import KeyManager, get_provider_default_model, get_service_providers
from multi_provider_handlers import get_handler

from config_utils import _EXE_DIR
PRESETS_FILE = os.path.join(_EXE_DIR, "genealogy_presets.json")


def get_genealogy_service_providers():
    return list(get_service_providers("ai_search"))


def get_genealogy_fallback_providers(key_manager, current_provider):
    return [
        provider
        for provider in get_genealogy_service_providers()
        if key_manager.get_all_keys(provider) and provider != current_provider
    ]

def extract_text_from_docx(docx_path):
    """Estrae il testo da un file .docx senza librerie esterne usando zipfile."""
    try:
        with zipfile.ZipFile(docx_path) as z:
            xml_content = z.read('word/document.xml')
            tree = ET.fromstring(xml_content)
            namespace = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
            paragraphs = tree.findall('.//w:t', namespace)
            return "".join([p.text for p in paragraphs if p.text])
    except Exception as e:
        return f"Errore DOCX: {str(e)}"


def _enrich_prompt_with_text(prompt: str, text_content: str) -> str:
    """
    Modalità Pipeline Due Fasi: inietta una trascrizione diplomatica nel prompt
    al posto dell'immagine. Valido per tutti i tipi documentali.
    """
    return (
        f"{prompt}\n\n"
        "NOTA OPERATIVA: Il documento non è un'immagine diretta ma una "
        "TRASCRIZIONE DIPLOMATICA prodotta in fase precedente con OCR Avanzato "
        "(paleografo specializzato). Il tuo compito è esclusivamente l'analisi "
        "strutturale e l'estrazione genealogica dal testo seguente — non devi "
        "eseguire OCR né interpretare grafia.\n\n"
        "--- TRASCRIZIONE DIPLOMATICA ---\n"
        f"{text_content.strip()}\n"
        "--- FINE TRASCRIZIONE ---\n"
    )

class GenealogyWorker(QThread):
    progress = Signal(int, str)
    finished = Signal(str, int)
    error = Signal(str)
    request_provider_change = Signal(str, list)

    def __init__(self, files, doc_type, tips, provider, output_file_path, base_path=None, custom_model=None, messages=None):
        super().__init__()
        self.custom_model = custom_model
        self.files = files
        self.doc_type = doc_type
        self.tips = tips
        self.provider = provider
        self.output_file_path = output_file_path
        self.base_path = base_path
        self.mutex = QMutex()
        self.wait_cond = QWaitCondition()
        self.provider_result = None
        self.messages = messages or {}

    def msg(self, key, **kwargs):
        template = self.messages.get(key, key)
        try:
            return template.format(**kwargs)
        except Exception:
            return template

    def run(self):
        try:
            # --- INIZIALIZZAZIONE TURBINA (Sincronia v5) ---
            km = KeyManager()
            current_prov = self.provider
            current_key, _ = km.get_next_key(current_prov)
            
            if not current_key:
                self.error.emit(self.msg("no_key", provider=current_prov)); return

            handler = get_handler(current_prov, current_key)
            generator = GedcomGenerator(source_system="ATK-Pro_Genealogy_Engine")
            
            effective_base = self.base_path
            if not effective_base and self.output_file_path:
                base_name = os.path.splitext(self.output_file_path)[0]
                csv_expected = f"{base_name}_REGISTRO_ORIGINALE.csv"
                if os.path.exists(self.output_file_path) or os.path.exists(csv_expected):
                    effective_base = self.output_file_path

            if effective_base:
                b_path = os.path.splitext(effective_base)[0]
                b_path = b_path.replace('_REGISTRO_ORIGINALE', '').replace('_REVISIONE_GENEALOGICA', '')
                ged_path = b_path + ".ged"
                csv_path = b_path + "_REGISTRO_ORIGINALE.csv"
                if os.path.exists(ged_path): generator.load_existing_gedcom(ged_path)
                if os.path.exists(csv_path): generator.load_existing_csv(csv_path)
            
            total_files = len(self.files)
            extracted_count = 0
            
            for i, file_path in enumerate(self.files):
                filename = os.path.basename(file_path).lower()
                percent = int((i / total_files) * 100)
                self.progress.emit(percent, self.msg("analysis_progress", current=i+1, total=total_files, filename=filename))
                
                success = False
                while not success:
                    try:
                        prompt = compose_extraction_prompt(self.doc_type, self.tips)
                        debug_dir = os.path.dirname(self.output_file_path)

                        # PIPELINE DUE FASI: se il file è una trascrizione (.txt/.docx),
                        # inietta il testo nel prompt e bypassa la pipeline immagine.
                        # Valido per tutti i tipi documentali.
                        file_ext = os.path.splitext(file_path)[1].lower()
                        effective_image_path = file_path
                        if file_ext == '.docx':
                            text_content = extract_text_from_docx(file_path)
                            prompt = _enrich_prompt_with_text(prompt, text_content)
                            effective_image_path = None
                        elif file_ext == '.txt':
                            with open(file_path, 'r', encoding='utf-8', errors='replace') as _tf:
                                text_content = _tf.read()
                            n_lines = text_content.count('\n') + 1
                            logging.debug(f"[TXT-READ] path={file_path!r} | chars={len(text_content)} | righe={n_lines} | anteprima={repr(text_content[:120])}")
                            prompt = _enrich_prompt_with_text(prompt, text_content)
                            effective_image_path = None

                        tx = handler.extract_genealogy(prompt, effective_image_path, model=self.custom_model, debug_dir=debug_dir)
                        if tx:
                            logging.debug(f"[{current_prov}] Estrazione completata: {len(str(tx))} chars")
                        # Se tx è già una lista (standard v36.9+: Gemini, Claude)
                        if isinstance(tx, list):
                            js = {"righe": tx}
                        elif isinstance(tx, dict):
                            js = tx
                        else:
                            # Fallback: tenta parsing JSON dal testo grezzo
                            tx_str = str(tx).strip()
                            arr_m = re.search(r"\[.*\]", tx_str, re.DOTALL)
                            obj_m = re.search(r"\{.*\}", tx_str, re.DOTALL)
                            raw = arr_m.group(0) if arr_m else (obj_m.group(0) if obj_m else tx_str)
                            js = json.loads(raw)
                            if isinstance(js, list):
                                js = {"righe": js}
                        
                        if hasattr(generator, 'parse_user_notes_metadata'):
                            generator.parse_user_notes_metadata(self.tips)

                        # Leggi il sidecar JSON dell'immagine per ottenere Source URL e Page
                        # Il sidecar è salvato da ATK-Pro accanto all'immagine con lo stesso nome base
                        sidecar_path = os.path.splitext(file_path)[0] + ".json"
                        if os.path.exists(sidecar_path):
                            try:
                                with open(sidecar_path, 'r', encoding='utf-8') as _sf:
                                    sidecar = json.load(_sf)
                                src_url = sidecar.get('Source', '')
                                page_lbl = sidecar.get('Page', '') or sidecar.get('PageLabel', '')
                                if src_url and hasattr(generator, 'set_canvas_source'):
                                    generator.set_canvas_source(src_url, page_label=page_lbl)
                            except Exception:
                                pass  # sidecar assente o malformato: procedi senza SOUR URL
                        # Collega l'immagine sorgente al canvas corrente → OBJE su ogni INDI
                        if effective_image_path and hasattr(generator, 'set_canvas_image'):
                            generator.set_canvas_image(effective_image_path)

                        generator.process_ai_json(js)
                        c_count = len(js.get('righe', js.get('records', [])))
                        if 'famiglie' in js:
                            c_count = sum(len(f.get('componenti', [])) for f in js['famiglie'])
                        extracted_count += c_count
                        success = True
                        
                    except Exception as e:
                        full_error = str(e)
                        key_hint = current_key[:6] + "..." if current_key else "None"
                        logging.error(f"[CAVEAU-FAIL] Chiave {key_hint} fallita: {full_error}")
                        
                        # Messaggio di stato pulito sulla barra
                        self.progress.emit(percent, self.msg("retry_next_key", provider=current_prov))
                        
                        next_key, wrapped = km.get_next_key(current_prov, current_key)
                        
                        if wrapped:
                            # Esaurite tutte le chiavi per questo provider (giro completo)
                            other_provs = get_genealogy_fallback_providers(km, current_prov)
                            if other_provs:
                                # SINCRO v5: Richiesta interattiva di cambio provider
                                self.mutex.lock()
                                self.provider_result = None
                                self.request_provider_change.emit(current_prov, other_provs)
                                self.wait_cond.wait(self.mutex)
                                self.mutex.unlock()
                                
                                if self.provider_result:
                                    current_prov = self.provider_result
                                    current_key, _ = km.get_next_key(current_prov)
                                    handler = get_handler(current_prov, current_key)
                                    self.progress.emit(percent, self.msg("provider_switch_confirmed", provider=current_prov))
                                    continue
                                else:
                                    self.error.emit(self.msg("provider_switch_cancelled")); return
                            else:
                                # Messaggio ancora più dettagliato in caso di fallimento totale
                                raise Exception(self.msg("total_vault_saturation", provider=current_prov, key_hint=key_hint, error=full_error))
                        
                        current_key = next_key
                        handler.set_key(current_key)
                        # SINCRO v15.4.6: Tempo di attesa ridotto per rotazione, ma aumentato per errori gravi
                        wait_time = 15 if "429" in full_error else 2
                        time.sleep(wait_time)

            generator.save_to_file(self.output_file_path)
            self.finished.emit(self.output_file_path, extracted_count)
        except Exception as e:
            self.error.emit(str(e))

class GenealogyDialog(QDialog):
    def __init__(self, parent=None, glossario=None, lingua="it"):
        super().__init__(parent)
        self.glossario = glossario
        self.lingua = lingua
        self.selected_files = []
        self.output_folder = ""
        self.base_path = None
        self.presets = {}
        self.init_ui()
        self.load_config()
        self.load_presets()

    def gm(self, chiave):
        try:
            from main_gui_qt import get_msg as _gm
            res = _gm(self.glossario, chiave, self.lingua)
            return res if res and res != chiave else chiave
        except Exception:
            return chiave

    def init_ui(self):
        self.setWindowTitle(f"{self.gm('Esportazione GEDCOM')} - ATK-Pro")
        self.setMinimumSize(950, 850)
        self.setStyleSheet("""
            QDialog { background-color: #181818; color: #fff; border: 2px solid #a67c52; }
            QLabel { color: #fff; font-size: 13px; font-weight: bold; }
            QPushButton { background-color: #222; border: 1px solid #a67c52; border-radius: 4px; padding: 10px; font-weight: bold; color: #fff; }
            QPushButton:hover { background-color: #333; }
            QComboBox, QLineEdit, QCheckBox { background-color: #2a2a2a; color: #fff; border: 1px solid #555; border-radius: 4px; padding: 7px; }
            QTextEdit { background-color: #2a2a2a; color: #ccc; border: 1px solid #555; border-radius: 4px; font-size: 14px; }
            QPushButton#btn_add_type { padding: 0px 0px 3px 0px; font-family: 'Segoe UI Symbol'; font-size: 13pt; color: #a67c52; }
            QPushButton#btn_edit_type { padding: 0px; font-family: 'Segoe UI Symbol'; font-size: 11pt; }
            QPushButton#btn_del_type { background-color: #2a1818; border-color: #8a3a3a; padding: 0px; font-family: 'Segoe UI Symbol'; font-size: 11pt; color: #cc6666; }
            QPushButton#btn_del_type:hover { background-color: #3a2020; }
        """)
        l = QVBoxLayout(self); l.setContentsMargins(18, 18, 18, 18)

        t_css = "color: #a67c52; font-size: 15px; font-weight: bold;"
        lbl_css = "font-size: 13px; font-weight: bold; color: #fff;"
        inp_css = "background-color: #2a2a2a; border: 1px solid #555; border-radius: 4px; padding: 7px; color: #fff;"
        btn_css = "QPushButton { background-color: #222; border: 1px solid #a67c52; border-radius: 4px; padding: 10px; font-weight: bold; color: #fff; } QPushButton:hover { background-color: #333; }"

        # --- Caveau chiavi in alto ---
        self.btn_manage_keys_top = QPushButton(f"🗝️ {self.gm('GESTISCI CAVEAU CHIAVI (CSV)')}")
        self.btn_manage_keys_top.setStyleSheet(btn_css)
        l.addWidget(self.btn_manage_keys_top)

        scroll = QScrollArea(); scroll.setWidgetResizable(True); scroll.setStyleSheet("QScrollArea { border: none; }")
        cont = QWidget(); fl = QVBoxLayout(cont); fl.setSpacing(18)

        # 1. INPUT UNIVERSALE
        fl.addWidget(QLabel(f"1. {self.gm('METODO E INPUT UNIVERSALE')}", styleSheet=t_css))
        f_in = QFormLayout(); self.combo_source = QComboBox(); self.combo_source.addItems(["Auto-Discovery", "Vision IA", "Refinery LLM"])
        self.combo_source.setStyleSheet(inp_css); f_in.addRow(QLabel(f"{self.gm('Metodo')}:", styleSheet=lbl_css), self.combo_source)
        browse_archive_label = self.gm("SFOGLIA L'ARCHIVIO")
        rs = QHBoxLayout(); self.btn_select = QPushButton(f"{browse_archive_label} 📂"); self.btn_select.setStyleSheet(btn_css); rs.addWidget(self.btn_select)
        self.lbl_count = QLabel(self.gm("{count} atti pronti").format(count=0)); self.lbl_count.setStyleSheet("color: #a67c52;"); rs.addWidget(self.lbl_count); rs.addStretch()
        f_in.addRow(QLabel(f"{self.gm('Input')}:", styleSheet=lbl_css), rs); fl.addLayout(f_in)

        # 2. BASE INCREMENTALE
        fl.addWidget(QLabel(f"2. {self.gm('INCREMENTA BASE ESISTENTE (GEDCOM o CSV)')}", styleSheet=t_css))
        rb = QHBoxLayout(); self.btn_load_base = QPushButton(f"{self.gm('CARICA BASE')} 🧬📑"); self.btn_load_base.setStyleSheet(btn_css); rb.addWidget(self.btn_load_base)
        self.lbl_base_path = QLabel(self.gm("Lavoro nuovo")); self.lbl_base_path.setStyleSheet("color: #a67c52; font-size: 11px;"); rb.addWidget(self.lbl_base_path); rb.addStretch(); fl.addLayout(rb)

        # 3. BANCA DATI NOTE
        fl.addWidget(QLabel(f"3. {self.gm('BANCA DATI NOTE PALEOGRAFICHE')}", styleSheet=t_css))
        ft = QFormLayout()
        from document_type_manager import DocumentTypeManager
        self._dtm = DocumentTypeManager()
        self.combo_type = QComboBox(); self.combo_type.addItems(self._dtm.get_labels(service="gedcom")); self.combo_type.setStyleSheet(inp_css)
        self.combo_type.currentIndexChanged.connect(self._on_type_changed_geo)
        btn_add_type_geo = QPushButton("+")
        btn_add_type_geo.setObjectName("btn_add_type")
        btn_add_type_geo.setToolTip(self.gm("Aggiungi tipologia personalizzata"))
        btn_add_type_geo.setFixedSize(30, 30)
        btn_add_type_geo.clicked.connect(self._add_custom_type)
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
        type_row = QHBoxLayout()
        type_row.addWidget(self.combo_type, 1)
        type_row.addWidget(btn_add_type_geo)
        type_row.addWidget(self.btn_edit_type)
        type_row.addWidget(self.btn_del_type)
        type_widget = QWidget(); type_widget.setLayout(type_row)
        ft.addRow(QLabel(f"{self.gm('Atto')}:", styleSheet=lbl_css), type_widget)
        self.combo_presets = QComboBox(); self.combo_presets.setStyleSheet(inp_css)
        ft.addRow(QLabel(f"{self.gm('Richiama Nota')}:", styleSheet=lbl_css), self.combo_presets); fl.addLayout(ft)
        self.txt_tips = QTextEdit(); self.txt_tips.setStyleSheet(inp_css); self.txt_tips.setMinimumHeight(120); fl.addWidget(self.txt_tips)
        rp = QHBoxLayout(); self.btn_save_p = QPushButton(f"💾 {self.gm('SALVA NOTA')}"); self.btn_save_p.setStyleSheet("background-color: #222; border: 1px solid #a67c52; color: #fff; padding: 10px; font-weight: bold;"); rp.addWidget(self.btn_save_p)
        self.btn_del_p = QPushButton(f"🗑️ {self.gm('ELIMINA')}"); self.btn_del_p.setStyleSheet("background-color: #2a1818; border: 1px solid #8a3a3a; color: #cc6666; padding: 10px; font-weight: bold;"); rp.addWidget(self.btn_del_p); fl.addLayout(rp)

        # 4. DESTINAZIONE
        fl.addWidget(QLabel(f"4. {self.gm('DESTINAZIONE OUTPUT')}", styleSheet=t_css))
        ro = QHBoxLayout(); self.btn_out = QPushButton(f"{self.gm('CARTELLA OUTPUT')} 📂"); self.btn_out.setStyleSheet(btn_css); ro.addWidget(self.btn_out)
        self.lbl_out_path = QLabel(self.gm("Output")); self.lbl_out_path.setStyleSheet("color: #a67c52;"); ro.addWidget(self.lbl_out_path); ro.addStretch(); fl.addLayout(ro)

        scroll.setWidget(cont); l.addWidget(scroll)
        
        # 5. MOTORE IA & CAVEAU
        fl.addWidget(QLabel(f"5. {self.gm('MOTORE IA & CAVEAU CHIAVI')}", styleSheet=t_css))
        fm = QFormLayout()
        self.combo_provider = QComboBox(); self.combo_provider.addItems(get_genealogy_service_providers()); self.combo_provider.setStyleSheet(inp_css)
        fm.addRow(QLabel(f"{self.gm('Provider')}:", styleSheet=lbl_css), self.combo_provider)
        
        self.inp_custom_model = QLineEdit()
        self.inp_custom_model.setStyleSheet(inp_css)
        self.lbl_custom_model = QLabel(f"{self.gm('Override Modello')}:", styleSheet=lbl_css)
        fm.addRow(self.lbl_custom_model, self.inp_custom_model)
        
        # Nascondi di default se Gemini
        self._toggle_custom_model()
        
        km_ly = QHBoxLayout()
        self.btn_manage_keys = QPushButton(f"🗝️ {self.gm('GESTISCI CAVEAU CHIAVI (CSV)')}"); self.btn_manage_keys.setStyleSheet(btn_css)
        km_ly.addWidget(self.btn_manage_keys); km_ly.addStretch()
        fm.addRow(QLabel(f"{self.gm('Chiavi')}:", styleSheet=lbl_css), km_ly)
        fl.addLayout(fm)

        self.progress_bar = QProgressBar(); self.progress_bar.setVisible(False); l.addWidget(self.progress_bar)
        self.btn_run = QPushButton(f"{self.gm('AVVIA ESTRAZIONE COMPLETA')} 🚀🧬"); self.btn_run.setMinimumHeight(60); self.btn_run.setStyleSheet("background-color: #a67c52; border: none; color: #fff; font-weight: bold; font-size: 16px; border-radius: 4px;"); l.addWidget(self.btn_run)

        # Connessioni
        self.btn_run.clicked.connect(self.start_process); self.btn_select.clicked.connect(self.select_files); self.btn_out.clicked.connect(self.select_output_folder)
        self.btn_load_base.clicked.connect(self.select_base_hybrid); self.btn_save_p.clicked.connect(self.save_current_preset); self.btn_del_p.clicked.connect(self.delete_selected_preset); self.combo_presets.currentIndexChanged.connect(self.apply_preset)
        self.btn_manage_keys_top.clicked.connect(self.open_key_manager)
        self.btn_manage_keys.clicked.connect(self.open_key_manager)
        self.combo_source.currentIndexChanged.connect(self.save_config)
        self.combo_type.currentIndexChanged.connect(self.save_config)
        self.combo_provider.currentIndexChanged.connect(self.save_config)
        self.combo_provider.currentIndexChanged.connect(self._toggle_custom_model)
        self.inp_custom_model.textChanged.connect(self.save_config)

    def _toggle_custom_model(self):
        prov = self.combo_provider.currentText()
        if prov == "Gemini":
            self.lbl_custom_model.setVisible(False)
            self.inp_custom_model.setVisible(False)
            self.inp_custom_model.clear()
        else:
            self.lbl_custom_model.setVisible(True)
            self.inp_custom_model.setVisible(True)
            self._update_custom_model_placeholder(prov)

    def _update_custom_model_placeholder(self, provider):
        default_model = get_provider_default_model(provider, "ai_search")
        if default_model:
            self.inp_custom_model.setPlaceholderText(
                self.gm("Es. {model} (lascia vuoto per default)").format(model=default_model)
            )
        else:
            self.inp_custom_model.setPlaceholderText(self.gm("Modello custom (opzionale)"))

    def _on_type_changed_geo(self):
        label = self.combo_type.currentText()
        is_custom = self._dtm.is_custom(label)
        self.btn_edit_type.setVisible(True)
        has_ov = not is_custom and self._dtm.has_builtin_override(label, "gedcom")
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
        dlg = NewDocTypeDialog(self, lingua=self.lingua, glossario_data=self.glossario)
        if dlg.exec() and dlg.result_data:
            ok = self._dtm.add_custom_type(**dlg.result_data)
            if ok:
                label = self._dtm.CUSTOM_PREFIX + dlg.result_data["label"]
                self.combo_type.addItem(label)
                self.combo_type.setCurrentText(label)
            else:
                from PySide6.QtWidgets import QMessageBox
                QMessageBox.warning(self, self.gm("Attenzione"), self.gm("Una tipologia con questo nome esiste già."))

    def _edit_custom_type(self):
        label = self.combo_type.currentText()
        if self._dtm.is_custom(label):
            data = self._dtm.get_custom_data(label)
            if not data:
                return
            from new_doc_type_dialog import NewDocTypeDialog
            dlg = NewDocTypeDialog(self, existing_data=data, lingua=self.lingua, glossario_data=self.glossario)
            if dlg.exec() and dlg.result_data:
                self._dtm.update_custom_type(**dlg.result_data)
        else:
            from prompt_edit_dialog import PromptEditDialog
            dlg = PromptEditDialog(self._dtm, label, "gedcom", parent=self,
                                   lingua=self.lingua, glossario_data=self.glossario)
            if dlg.exec():
                self._on_type_changed_geo()

    def _delete_custom_type(self):
        from PySide6.QtWidgets import QMessageBox
        label = self.combo_type.currentText()
        msg = QMessageBox(self)
        msg.setWindowTitle(self.gm("Elimina Tipologia"))
        msg.setText((self.gm("Rimuovere '%s' dalla lista?") % label))
        btn_si = msg.addButton(self.gm("Si"), QMessageBox.ButtonRole.YesRole)
        msg.addButton(self.gm("No"), QMessageBox.ButtonRole.NoRole)
        msg.exec()
        if msg.clickedButton() == btn_si:
            self._dtm.delete_custom_type(label)
            idx = self.combo_type.findText(label)
            if idx >= 0:
                self.combo_type.removeItem(idx)

    def load_config(self):
        try:
            from config_utils import _config_file_path
            p = _config_file_path()
            logging.info(f"[SINCRO] Tento caricamento config da: {p}")
            if os.path.exists(p):
                with open(p, "r", encoding="utf-8") as f:
                    c = json.load(f)
                    self.output_folder = c.get("output_folder_single", os.getcwd())
                    self.lbl_out_path.setText(self.output_folder)
                    # Sincro v15.6: Ripristino ultime impostazioni
                    if c.get("last_doc_type"): self.combo_type.setCurrentText(c["last_doc_type"])
                    if c.get("last_tips"): self.txt_tips.setPlainText(c["last_tips"])
                    if c.get("last_provider"): self.combo_provider.setCurrentText(c["last_provider"])
                    if c.get("last_custom_model"): self.inp_custom_model.setText(c["last_custom_model"])
                    if c.get("last_source"): self.combo_source.setCurrentText(c["last_source"])
                    if c.get("last_base_path") and os.path.exists(c["last_base_path"]):
                        self.base_path = c["last_base_path"]
                        self.lbl_base_path.setText(os.path.basename(self.base_path))
                    logging.info(f"[SINCRO] Config caricato correttamente. Base: {self.base_path}")
        except Exception as e:
            logging.error(f"[SINCRO] Errore caricamento config: {e}")
        except: pass

    def save_config(self):
        """Salva le impostazioni correnti per il prossimo avvio."""
        try:
            from main_gui_qt import _config_file_path
            p = _config_file_path()
            data = {}
            if os.path.exists(p):
                with open(p, "r", encoding="utf-8") as f: data = json.load(f)
            
            data["output_folder_single"] = self.output_folder
            data["last_doc_type"] = self.combo_type.currentText()
            data["last_tips"] = self.txt_tips.toPlainText()
            data["last_provider"] = self.combo_provider.currentText()
            data["last_custom_model"] = self.inp_custom_model.text().strip()
            data["last_source"] = self.combo_source.currentText()
            if self.base_path:
                data["last_base_path"] = self.base_path
            
            logging.info(f"[SINCRO] Config salvato in {p}. Base: {self.base_path}")
            with open(p, "w", encoding="utf-8") as f: json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logging.error(f"[SINCRO] Errore salvataggio config: {e}")
        except: pass

    def load_presets(self):
        self.combo_presets.clear(); self.combo_presets.addItem(f"--- {self.gm('Carica Nota dalla Banca Dati')} ---")
        try:
            if os.path.exists(PRESETS_FILE):
                with open(PRESETS_FILE, "r", encoding="utf-8") as f:
                    self.presets = json.load(f)
                    for k in sorted(self.presets.keys()): self.combo_presets.addItem(k)
        except: self.presets = {}

    def save_current_preset(self):
        t = self.txt_tips.toPlainText().strip()
        if not t: return
        n, ok = QInputDialog.getText(self, self.gm("Salva"), self.gm("Nome nota:"))
        if ok and n: self.presets[n] = t; self.save_pf(); self.load_presets()

    def save_pf(self):
        with open(PRESETS_FILE, "w", encoding="utf-8") as f: json.dump(self.presets, f, indent=4)

    def apply_preset(self):
        p = self.combo_presets.currentText()
        if p in self.presets: self.txt_tips.setPlainText(self.presets[p])

    def delete_selected_preset(self):
        p = self.combo_presets.currentText()
        if p in self.presets:
            if QMessageBox.question(self, self.gm("Elimina"), self.gm("Rimuovere '%s' dalla lista?") % p) == QMessageBox.Yes:
                del self.presets[p]; self.save_pf(); self.load_presets()

    def select_output_folder(self):
        f = QFileDialog.getExistingDirectory(self, self.gm("Seleziona"), self.output_folder)
        if f: self.output_folder = f; self.lbl_out_path.setText(f)

    def select_base_hybrid(self):
        p, _ = QFileDialog.getOpenFileName(self, self.gm("Base"), "", f"{self.gm('Database')} (*.ged *.csv)")
        if p: 
            self.base_path = p
            self.lbl_base_path.setText(os.path.basename(p))
            self.save_config() # Salva subito il percorso della base

    def select_files(self):
        f, _ = QFileDialog.getOpenFileNames(self, self.gm("Seleziona"), "", f"{self.gm('Archivio')} (*.pdf *.docx *.jpg *.jpeg *.png *.webp *.tiff *.tif *.bmp *.txt *.json *.csv)")
        if f: self.selected_files = f; self.lbl_count.setText(self.gm("{count} file pronti").format(count=len(f)))

    def _worker_messages(self):
        return {
            "no_key": self.gm("Nessuna chiave trovata per {provider} nel Caveau (api_keys.csv)!"),
            "analysis_progress": self.gm("Analisi {current}/{total}: {filename}"),
            "retry_next_key": self.gm("Errore {provider}: riprovo con la prossima chiave..."),
            "provider_switch_confirmed": self.gm("Passaggio a {provider} confermato. Riprovo..."),
            "provider_switch_cancelled": self.gm("Operazione annullata o nessun provider disponibile selezionato."),
            "total_vault_saturation": self.gm("Saturazione Totale Caveau.\nUltimo errore per {provider} (chiave {key_hint}):\n{error}"),
        }

    def start_process(self):
        if not self.selected_files: return
        self.save_config()
        # SINCRO v48.2: Forza il salvataggio nella cartella della BASE se presente
        if self.base_path:
            self.output_folder = os.path.dirname(self.base_path)
            logging.info(f"[SINCRO] Output dirottato su cartella Base: {self.output_folder}")

        # SINCRO v15.1: Bonifica caratteri illegali per Windows (/)
        doc_type_raw = self.combo_type.currentText()
        tag = doc_type_raw.replace(" ", "_").replace("/", "_").replace("★ ", "").lower()
        fp = os.path.join(self.output_folder, f"genealogia_{tag}.ged")
        self.btn_run.setEnabled(False); self.progress_bar.setVisible(True); self.progress_bar.setValue(1)
        # Per tipi custom, inietta il prompt gedcom nei tips aggiuntivi
        tips_text = self.txt_tips.toPlainText()
        if self._dtm.is_custom(doc_type_raw):
            custom_gedcom = self._dtm.get_gedcom_prompt(doc_type_raw) or ""
            if custom_gedcom:
                tips_text = custom_gedcom + ("\n" + tips_text if tips_text else "")
            doc_type_raw = "Ricerca Libera / Altro"  # fallback built-in nel worker
        self.worker = GenealogyWorker(self.selected_files, doc_type_raw, tips_text, self.combo_provider.currentText(), fp, self.base_path, custom_model=self.inp_custom_model.text().strip(), messages=self._worker_messages())
        self.worker.progress.connect(lambda v,m: (self.progress_bar.setValue(v), self.progress_bar.setFormat(m)))
        self.worker.request_provider_change.connect(self.handle_provider_change)
        self.worker.finished.connect(self.process_finished); self.worker.error.connect(self.process_error); self.worker.start()

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

    def handle_provider_change(self, current_prov, available_provs):
        """Slot per gestire la richiesta di cambio provider interattivo."""
        msg = self.gm("Le chiavi di {provider} sono sature.\nVuoi passare a un altro provider disponibile?").format(provider=current_prov)
        box = QMessageBox(self)
        box.setWindowTitle(self.gm("Saturazione API"))
        box.setText(msg)
        box.setIcon(QMessageBox.Question)
        
        btns = {}
        for p in available_provs:
            b = box.addButton(self.gm("Usa {provider}").format(provider=p), QMessageBox.AcceptRole)
            btns[b] = p
        
        cancel = box.addButton(self.gm("Annulla"), QMessageBox.RejectRole)
        box.exec()
        
        if box.clickedButton() in btns:
            self.worker.provider_result = btns[box.clickedButton()]
            # Sincronizza visivamente il dropdown
            self.combo_provider.setCurrentText(self.worker.provider_result)
        else:
            self.worker.provider_result = None
            
        self.worker.wait_cond.wakeAll()

    def process_finished(self, p, c):
        self.btn_run.setEnabled(True); self.progress_bar.setVisible(False)
        QMessageBox.information(self, self.gm("Completato"), self.gm("Finito!\nFile: {file}\nRecord: {count}").format(file=p, count=c))

    def process_error(self, e):
        self.btn_run.setEnabled(True); QMessageBox.critical(self, self.gm("Stato Quota"), str(e))
