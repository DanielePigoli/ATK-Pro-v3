import logging
import os
LOG_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'atkpro_debug.log'))
if not logging.getLogger('atkpro').hasHandlers():
    handler = logging.FileHandler(LOG_PATH, encoding='utf-8')
    handler.setFormatter(logging.Formatter('[%(asctime)s][%(levelname)s][%(name)s] %(message)s'))
    logging.getLogger('atkpro').addHandler(handler)
    logging.getLogger('atkpro').setLevel(logging.DEBUG)
logger = logging.getLogger('atkpro')
import os
import threading
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QComboBox, QCheckBox, QLineEdit, QFileDialog, QProgressBar, QMessageBox, QApplication, QTextEdit, QScrollArea, QGraphicsView, QInputDialog
)
from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import QIcon, QFont, QPixmap

from asset_cache import get_pixmap_cached
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

from ocr_processor import AdvancedOCRWorker

def get_msg(glossario, chiave, lingua):
    try:
        from main_gui_qt import get_msg as _get_msg
        return _get_msg(glossario, chiave, lingua)
    except:
        return chiave

def asset_path(rel_path):
    try:
        from main_gui_qt import asset_path as _asset_path
        return _asset_path(rel_path)
    except:
        return rel_path

class ZoomableView(QGraphicsView):
    def __init__(self, pixmap, parent=None):
        from PySide6.QtWidgets import QGraphicsScene
        from PySide6.QtGui import QPainter
        super().__init__(parent)
        self.scene = QGraphicsScene(self)
        self.item = self.scene.addPixmap(pixmap)
        self.setScene(self.scene)
        self.setDragMode(QGraphicsView.ScrollHandDrag)
        self.setRenderHint(QPainter.Antialiasing)
        self.setRenderHint(QPainter.SmoothPixmapTransform)
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.AnchorUnderMouse)
        self.fitInView(self.item, Qt.KeepAspectRatio)

    def wheelEvent(self, event):
        zoom_in_factor = 1.25
        zoom_out_factor = 1 / zoom_in_factor
        if event.angleDelta().y() > 0:
            zoom_factor = zoom_in_factor
        else:
            zoom_factor = zoom_out_factor
        self.scale(zoom_factor, zoom_factor)

class OCRReviewDialog(QDialog):
    def __init__(self, img_path, raw_text, parent=None, lingua=None, glossario_data=None,
                 ok_label=None, skip_label=None, title=None):
        super().__init__(parent)
        self.lingua = (lingua or "it").upper()
        self.glossario_data = glossario_data
        self.setWindowTitle(title if title else self.gm("Revisione Interattiva OCR"))
        from PySide6.QtCore import Qt
        self.setWindowFlags(
            Qt.Window |
            Qt.WindowTitleHint |
            Qt.WindowMinMaxButtonsHint |
            Qt.WindowCloseButtonHint
        )
        self.setMinimumSize(900, 600)
        self.resize(1100, 750)

        self.setStyleSheet("""
            QDialog { background-color: #181818; color: #fff; border: 2px solid #a67c52; }
            QLabel { color: #fff; font-size: 14px; }
            QPushButton { background-color: #222; border: 1px solid #a67c52; padding: 6px 18px; border-radius: 6px; font-weight: bold; color: #fff; }
            QPushButton:hover { background-color: #333; }
            QTextEdit { background-color: #2a2a2a; color: #ccc; border: 1px solid #555; border-radius: 4px; font-size: 14px; }
        """)

        layout = QHBoxLayout(self)

        # Left side: Image Viewer
        pix = QPixmap(img_path)
        if not pix.isNull():
            self.zoom_view = ZoomableView(pix)
            self.zoom_view.setStyleSheet("background-color: #2a2a2a; border: 1px solid #555;")
            layout.addWidget(self.zoom_view, 1)
        else:
            lbl = QLabel(self.gm("Immagine non disponibile"))
            lbl.setAlignment(Qt.AlignCenter)
            layout.addWidget(lbl, 1)

        # Right side: Editor + Buttons
        right_ly = QVBoxLayout()
        lbl_info = QLabel(self.gm("Correggi il testo e clicca 'Approva' per salvare:"))
        lbl_info.setStyleSheet("color: #e6c891; font-weight: bold;")
        self.txt_editor = QTextEdit()
        self.txt_editor.setPlainText(raw_text)

        btn_ly = QHBoxLayout()
        btn_skip = QPushButton(skip_label if skip_label else self.gm("Salta Pagina"))
        btn_skip.clicked.connect(self.reject)
        btn_ok = QPushButton(ok_label if ok_label else self.gm("Approva e Genera File"))
        btn_ok.setStyleSheet("background-color: #a67c52; color: #fff; padding: 8px;")
        btn_ok.clicked.connect(self.accept)

        btn_ly.addWidget(btn_skip)
        btn_ly.addWidget(btn_ok)

        right_ly.addWidget(lbl_info)
        right_ly.addWidget(self.txt_editor)
        right_ly.addLayout(btn_ly)

        layout.addLayout(right_ly, 1)

    def gm(self, text):
        res = get_msg(self.glossario_data, text, self.lingua)
        return res if (res and res != text) else text

class OCRThread(QThread):
    progress = Signal(int, int, str)
    finished = Signal(bool, str)
    review_requested = Signal(str, str)

    def __init__(self, file_paths, provider, api_key, formats, output_dir, prefix_elab="Elaborazione: ", custom_prompt="", example_text="", interactive=False, custom_model=None):
        super().__init__()
        self.custom_model = custom_model
        self.file_paths = file_paths
        self.provider = provider
        self.api_key = api_key
        self.formats = formats
        self.output_dir = output_dir
        self.prefix_elab = prefix_elab
        self.custom_prompt = custom_prompt
        self.example_text = example_text
        self.interactive = interactive
        self.review_event = threading.Event()
        self.reviewed_text = None

    def run(self):
        try:
            worker = AdvancedOCRWorker(self.provider, self.api_key, self.formats, self.output_dir, self.custom_prompt, self.example_text, custom_model=self.custom_model)
            
            def interceptor(img_path, raw_text):
                if not self.interactive:
                    return raw_text
                self.reviewed_text = None
                self.review_requested.emit(img_path, raw_text)
                self.review_event.wait()
                self.review_event.clear()
                return self.reviewed_text
                
            total = len(self.file_paths)
            for i, f_path in enumerate(self.file_paths):
                fname = os.path.basename(f_path)
                self.progress.emit(i, total, f"{self.prefix_elab}{fname}")

                # Callback per il progresso pagina-per-pagina dei PDF
                file_idx, total_files, file_name = i, total, fname
                def make_page_cb(fi, tf, fn):
                    def cb(page_num, n_pages):
                        self.progress.emit(fi, tf, f"{fn} — pag. {page_num}/{n_pages}")
                    return cb

                worker.process_file(f_path, review_callback=interceptor,
                                    page_progress=make_page_cb(file_idx, total_files, file_name))
            self.progress.emit(total, total, "Completato")
            self.finished.emit(True, "Estrazione OCR completata con successo.")
        except Exception as e:
            self.finished.emit(False, str(e))


class CalibrationThread(QThread):
    """Thread che elabora solo il TOP 60% del primo file per la calibrazione assistita."""
    preview_ready = Signal(str, str)  # (tmp_img_path, testo_raw)
    error = Signal(str)

    def __init__(self, file_path, provider, api_key, base_prompt):
        super().__init__()
        self.file_path = file_path
        self.provider = provider
        self.api_key = api_key
        self.base_prompt = base_prompt

    def run(self):
        try:
            worker = AdvancedOCRWorker(self.provider, self.api_key, [], None)
            last_error = None
            for attempt in range(len(worker.api_keys)):
                try:
                    tmp_path, text = worker.transcribe_top_preview(
                        self.file_path, worker._current_key(), self.base_prompt
                    )
                    self.preview_ready.emit(tmp_path, text)
                    return
                except Exception as e:
                    err_str = str(e).lower()
                    last_error = e
                    is_quota = any(k in err_str for k in ["429", "quota", "resource_exhausted", "rate"])
                    if is_quota:
                        if not worker._rotate_key():
                            break
                    else:
                        raise e
            self.error.emit(str(last_error))
        except Exception as e:
            self.error.emit(str(e))


class AdvancedOCRDialog(QDialog):
    def __init__(self, parent=None, glossario_data=None, lingua="it"):
        logger.debug("[AdvancedOCRDialog] __init__ INIZIO")
        super().__init__(parent)
        self.glossario_data = glossario_data
        self.lingua = lingua
        self.file_paths = []
        self.saved_instructions = {}  # {nome: testo}
        try:
            self.setup_ui()
            logger.debug("[AdvancedOCRDialog] setup_ui COMPLETATA")
            # Carica impostazioni solo dopo che tutti i controlli sono creati
            try:
                self.load_settings()
            except Exception as e:
                logger.error(f"[AdvancedOCRDialog] Errore in load_settings: {e}")
        except Exception as e:
            import traceback
            logger.error(f"[AdvancedOCRDialog] ECCEZIONE in setup_ui: {e}\n" + traceback.format_exc())
            raise

    def gm(self, text):
        res = get_msg(self.glossario_data, text, self.lingua)
        return res if (res and res != text) else text

    def _current_provider_key(self):
        return normalize_provider_name(self.combo_prov.currentText())

    def setup_ui(self):
        logger.debug("[AdvancedOCRDialog] setup_ui INIZIO")
        self.setWindowTitle(self.gm("OCR Avanzato (Trascrizione Diplomatica)"))
        self.setMinimumSize(900, 600)
        self.setWindowFlags(self.windowFlags() | Qt.WindowMinimizeButtonHint | Qt.WindowMaximizeButtonHint)
        self.resize(950, 700)
        self.setStyleSheet("""
            QDialog { background-color: #181818; color: #fff; border: 2px solid #a67c52; }
            QLabel { color: #fff; font-size: 14px; }
            QPushButton { background-color: #222; border: 1px solid #a67c52; padding: 6px 18px; border-radius: 6px; font-weight: bold; color: #fff; }
            QPushButton:hover { background-color: #333; }
            QComboBox, QLineEdit, QCheckBox { background-color: #2a2a2a; color: #fff; padding: 4px; border: 1px solid #555; border-radius: 4px; }
            QTextEdit { background-color: #2a2a2a; color: #ccc; border: 1px solid #555; border-radius: 4px; }
            QPushButton#btn_add_type { padding: 0px 0px 3px 0px; font-family: 'Segoe UI Symbol'; font-size: 13pt; color: #a67c52; }
            QPushButton#btn_edit_type { padding: 0px; font-family: 'Segoe UI Symbol'; font-size: 11pt; }
            QPushButton#btn_del_type { background-color: #2a1818; border-color: #8a3a3a; padding: 0px; font-family: 'Segoe UI Symbol'; font-size: 11pt; color: #cc6666; }
            QPushButton#btn_del_type:hover { background-color: #3a2020; }
        """)

        layout = QVBoxLayout(self)
        # --- Caveau chiavi (come GenealogyDialog) ---
        # RIMOSSO pulsante gestione caveau chiavi: già presente Cassaforte accanto all'API Key

        # File Selection
        lbl_file = QLabel(self.gm("File Selezionati:"))
        self.lbl_file_path = QLabel(self.gm("Nessun file selezionato"))
        self.lbl_file_path.setWordWrap(True)
        btn_sel = QPushButton(self.gm("Seleziona File (Immagini/PDF)"))
        btn_sel.clicked.connect(self.select_files)
        file_layout = QHBoxLayout()
        file_layout.addWidget(lbl_file)
        file_layout.addWidget(self.lbl_file_path)
        file_layout.addWidget(btn_sel)
        layout.addLayout(file_layout)

        # Tipologia Documentale
        from document_type_manager import DocumentTypeManager
        self._dtm = DocumentTypeManager()
        type_layout = QHBoxLayout()
        lbl_type = QLabel(self.gm("Tipologia Documento:"))
        lbl_type.setStyleSheet("font-weight: bold;")
        self.combo_type = QComboBox()
        self.combo_type.addItems(self._dtm.get_labels(service="ocr"))
        self.combo_type.currentIndexChanged.connect(self._on_type_changed_ocr)
        btn_add_type = QPushButton("+")
        btn_add_type.setObjectName("btn_add_type")
        btn_add_type.setToolTip(self.gm("Aggiungi tipologia personalizzata"))
        btn_add_type.setFixedSize(30, 30)
        btn_add_type.clicked.connect(self._add_custom_type)
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
        type_layout.addWidget(lbl_type)
        type_layout.addWidget(self.combo_type, 1)
        type_layout.addWidget(btn_add_type)
        type_layout.addWidget(self.btn_edit_type)
        type_layout.addWidget(self.btn_del_type)
        layout.addLayout(type_layout)

        # Provider Selection
        lbl_prov = QLabel(self.gm("Seleziona Provider IA:"))
        self.combo_prov = QComboBox()
        self.combo_prov.addItems([
            "Anthropic / Claude (Miglior Vision)",
            "OpenAI (GPT-4o Vision)",
            "Google Gemini (Vision)",
            "Transkribus (Italian Handwriting HTR)",
            "Hugging Face (Modelli Specializzati OCR)",
            "xAI / Grok (Vision)",
            "Mistral (Pixtral Vision)",
            "Groq (Llama Vision)",
            "Ollama (Locale/Privato)",
            "DeepSeek (Solo Testo)"
        ])
        self.combo_prov.currentIndexChanged.connect(self.provider_changed)
        layout.addWidget(lbl_prov)
        layout.addWidget(self.combo_prov)

        self.lbl_custom_model = QLabel(self.gm("Override Modello (opzionale):"))
        self.inp_custom_model = QLineEdit()
        self.inp_custom_model.setPlaceholderText(self.gm("Es. gpt-5-preview (lascia vuoto per default)"))
        layout.addWidget(self.lbl_custom_model)
        layout.addWidget(self.inp_custom_model)

        # API Key
        self.lbl_api = QLabel(self.gm("API Key per il provider scelto:"))
        api_ly = QHBoxLayout()
        self.txt_api = QLineEdit()
        self.txt_api.setEchoMode(QLineEdit.Password)
        btn_key_safe = QPushButton("🔑 " + self.gm("Cassaforte"))
        btn_key_safe.setStyleSheet("background-color: #2a2a2a; color: #f5f0e8; border: 1px solid #888; padding: 2px 10px; border-radius: 4px; font-size: 11px;")
        btn_key_safe.clicked.connect(self.open_key_manager)
        api_ly.addWidget(self.txt_api)
        api_ly.addWidget(btn_key_safe)
        layout.addWidget(self.lbl_api)
        layout.addLayout(api_ly)
        # Inizializza visibilità
        self.provider_changed()

        # Formats
        lbl_fmt = QLabel(self.gm("Formati di Output:"))
        self.chk_txt = QCheckBox(self.gm("Testo Semplice (.txt)"))
        self.chk_docx = QCheckBox(self.gm("Documento Word (.docx)"))
        self.chk_xml = QCheckBox(self.gm("XML TEI per Trascrizione (.xml)"))
        self.chk_txt.setChecked(True)
        self.chk_docx.setChecked(True)
        self.chk_xml.setChecked(True)
        fmt_layout = QHBoxLayout()
        fmt_layout.addWidget(self.chk_txt)
        fmt_layout.addWidget(self.chk_docx)
        fmt_layout.addWidget(self.chk_xml)
        layout.addWidget(lbl_fmt)
        layout.addLayout(fmt_layout)

        # Revisione Interattiva Checkbox
        self.chk_interactive = QCheckBox(self.gm("Abilita Finestra di Revisione Interattiva prima di salvare l'OCR"))
        self.chk_interactive.setStyleSheet("color: #f5f0e8; font-weight: bold; margin-top: 5px; margin-bottom: 5px;")
        layout.addWidget(self.chk_interactive)

        # Calibrazione Assistita Checkbox
        self.chk_calibration = QCheckBox(self.gm("Abilita Calibrazione Assistita (anteprima TOP per creare il riferimento)"))
        self.chk_calibration.setStyleSheet("color: #c8e6c9; font-weight: bold; margin-bottom: 5px;")
        self.chk_calibration.setToolTip(
            self.gm(
                "Il programma elabora le prime righe, le mostra per correzione,\n"
                "poi usa il testo corretto come riferimento per l'elaborazione completa."
            )
        )
        layout.addWidget(self.chk_calibration)

        # Istruzioni extra con Archiviazione
        istr_header_ly = QHBoxLayout()
        lbl_istruzioni = QLabel(self.gm("Istruzioni Aggiuntive per l'IA (Opzionale):"))
        lbl_istruzioni.setStyleSheet("margin-top: 10px; color: #f5f0e8; font-weight: bold;")

        self.combo_istruzioni = QComboBox()
        self.combo_istruzioni.addItem(self.gm("-- Istruzioni Salvate --"), "")
        self.combo_istruzioni.currentIndexChanged.connect(self.load_saved_instruction)

        _btn_small = "background-color: #222; border: 1px solid #a67c52; border-radius: 4px; font-weight: bold; color: #a67c52; padding: 0px; font-size: 14px;"
        self.btn_add_istruzione = QPushButton("+")
        self.btn_add_istruzione.setToolTip(self.gm("Salva istruzione corrente con un nome"))
        self.btn_add_istruzione.setFixedSize(26, 26)
        self.btn_add_istruzione.setStyleSheet(_btn_small)
        self.btn_add_istruzione.clicked.connect(self.add_instruction)

        self.btn_ren_istruzione = QPushButton()
        self.btn_ren_istruzione.setText("✏")
        self.btn_ren_istruzione.setToolTip(self.gm("Rinomina istruzione selezionata"))
        self.btn_ren_istruzione.setFixedSize(26, 26)
        self.btn_ren_istruzione.setStyleSheet(_btn_small)
        self.btn_ren_istruzione.clicked.connect(self.rename_instruction)

        self.btn_del_istruzione = QPushButton()
        self.btn_del_istruzione.setText("✕")
        self.btn_del_istruzione.setToolTip(self.gm("Elimina istruzione selezionata"))
        self.btn_del_istruzione.setFixedSize(26, 26)
        self.btn_del_istruzione.setStyleSheet("background-color: #2a1818; border: 1px solid #8a3a3a; border-radius: 4px; font-weight: bold; color: #cc6666; padding: 0px; font-size: 14px;")
        self.btn_del_istruzione.clicked.connect(self.delete_instruction)

        istr_header_ly.addWidget(lbl_istruzioni)
        istr_header_ly.addStretch()
        istr_header_ly.addWidget(self.combo_istruzioni)
        istr_header_ly.addWidget(self.btn_add_istruzione)
        istr_header_ly.addWidget(self.btn_ren_istruzione)
        istr_header_ly.addWidget(self.btn_del_istruzione)

        layout.addLayout(istr_header_ly)

        self.txt_istruzioni = QTextEdit()
        self.txt_istruzioni.setAcceptRichText(False)
        self.txt_istruzioni.setPlaceholderText(self.gm("Es: I nomi dei mesi sono in dialetto, ometti i timbri a margine..."))
        self.txt_istruzioni.setMaximumHeight(60)
        layout.addWidget(self.txt_istruzioni)

        # Trascrizione di Esempio (Few-Shot)
        es_header_ly = QHBoxLayout()
        lbl_esempio = QLabel(self.gm("Trascrizione di Riferimento (Opzionale):"))
        lbl_esempio.setStyleSheet("margin-top: 5px; color: #f5f0e8; font-weight: bold;")

        self.btn_clear_esempio = QPushButton("✖ " + self.gm("Cancella Testo"))
        self.btn_clear_esempio.setStyleSheet("background-color: #5a1a1a; color: #fff; padding: 2px 10px; border-radius: 4px; font-size: 11px;")
        self.btn_clear_esempio.clicked.connect(lambda: self.txt_esempio.clear())

        es_header_ly.addWidget(lbl_esempio)
        es_header_ly.addStretch()
        es_header_ly.addWidget(self.btn_clear_esempio)

        self.txt_esempio = QTextEdit()
        self.txt_esempio.setAcceptRichText(False)
        self.txt_esempio.setPlaceholderText(self.gm("Copia qui la trascrizione esatta della primissima pagina per addestrare l'IA."))
        self.txt_esempio.setMaximumHeight(80)

        layout.addLayout(es_header_ly)
        layout.addWidget(self.txt_esempio)

        # Progress
        self.progress_lbl = QLabel()
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        layout.addWidget(self.progress_lbl)
        layout.addWidget(self.progress_bar)

        # Start/Close
        btns = QHBoxLayout()
        self.btn_start = QPushButton(self.gm("Avvia OCR"))
        self.btn_start.clicked.connect(self.start_ocr)
        self.btn_close = QPushButton(self.gm("Chiudi"))
        self.btn_close.clicked.connect(self.reject)
        btns.addWidget(self.btn_start)
        btns.addWidget(self.btn_close)
        layout.addLayout(btns)

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

    def _on_type_changed_ocr(self):
        """Mostra/nasconde i pulsanti Modifica/Elimina in base al tipo selezionato."""
        label = self.combo_type.currentText()
        is_custom = self._dtm.is_custom(label)
        # ✏ visibile sempre: per built-in apre editor prompt, per custom apre NewDocTypeDialog
        self.btn_edit_type.setVisible(True)
        # indica override attivo con colore diverso
        has_ov = not is_custom and self._dtm.has_builtin_override(label, "ocr")
        self.btn_edit_type.setStyleSheet(
            "background-color: #2a2a1a; border: 1px solid #cc9922; color: #ffcc44;"
            if has_ov else ""
        )
        self.btn_edit_type.setToolTip(
            self.gm("Override prompt attivo — clicca per modificare") if has_ov
            else self.gm("Modifica prompt tipologia selezionata")
        )
        # ✕ solo per custom
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
            # Custom: apre NewDocTypeDialog come prima
            data = self._dtm.get_custom_data(label)
            if not data:
                return
            from new_doc_type_dialog import NewDocTypeDialog
            dlg = NewDocTypeDialog(self, existing_data=data, lingua=self.lingua, glossario_data=self.glossario_data)
            if dlg.exec() and dlg.result_data:
                self._dtm.update_custom_type(**dlg.result_data)
        else:
            # Built-in: apre editor prompt con supporto override
            from prompt_edit_dialog import PromptEditDialog
            dlg = PromptEditDialog(self._dtm, label, "ocr", parent=self,
                                   lingua=self.lingua, glossario_data=self.glossario_data)
            if dlg.exec():
                # Aggiorna stile pulsante (override potrebbe essere stato salvato o rimosso)
                self._on_type_changed_ocr()

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

    def open_key_manager(self):
        from key_manager import KeyManager
        km = KeyManager()
        import platform, subprocess
        if os.path.exists(km.file_path):
            try:
                if platform.system() == 'Windows': os.startfile(km.file_path)
                elif platform.system() == 'Darwin': subprocess.run(['open', km.file_path])
                else: subprocess.run(['xdg-open', km.file_path])
            except Exception:
                QMessageBox.warning(self, self.gm("Errore"), self.gm("Impossibile aprire il file CSV."))
        else:
            QMessageBox.warning(self, self.gm("Errore"), self.gm("File chiavi non trovato."))

    def select_files(self):
        files, _ = QFileDialog.getOpenFileNames(
            self, self.gm("Seleziona Immagini o PDF"), "",
            f"{self.gm('Documenti')} ( *.pdf *.png *.jpg *.jpeg *.tiff *.tif )"
        )
        if files:
            self.file_paths = files
            self.lbl_file_path.setText(f"{len(files)} " + self.gm("file selezionati"))

    def provider_changed(self):
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
        elif "Mistral" in prov:
            self.lbl_api.setText(self.gm("Mistral API Key:"))
            self.lbl_custom_model.setVisible(True)
            self.inp_custom_model.setVisible(True)
        elif "Groq" in prov:
            self.lbl_api.setText(self.gm("Groq API Key:"))
            self.lbl_custom_model.setVisible(True)
            self.inp_custom_model.setVisible(True)
        elif "DeepSeek" in prov:
            self.lbl_api.setText(self.gm("DeepSeek API Key:"))
            self.lbl_custom_model.setVisible(True)
            self.inp_custom_model.setVisible(True)
        elif "xAI" in prov:
            self.lbl_api.setText(self.gm("xAI API Key:"))
            self.lbl_custom_model.setVisible(True)
            self.inp_custom_model.setVisible(True)
        elif "Ollama" in prov:
            self.lbl_api.setText(self.gm("Host Ollama (es. http://localhost:11434):"))
            self.lbl_custom_model.setVisible(True)
            self.inp_custom_model.setPlaceholderText(self.gm("Es. llava, llama3.2-vision, qwen2.5vl"))
            self.inp_custom_model.setVisible(True)
            current_api = self.txt_api.text().strip()
            if current_api and not current_api.lower().startswith(("http://", "https://")):
                self.txt_api.clear()
            self.txt_api.setPlaceholderText("http://localhost:11434")
        elif "Hugging Face" in prov:
            self.lbl_api.setText(self.gm("Hugging Face Token (hf_...):"))
            self.lbl_custom_model.setVisible(True)
            self.inp_custom_model.setPlaceholderText(self.gm("Es. microsoft/trocr-large-handwritten, stepfun-ai/GOT-OCR2_0"))
            self.inp_custom_model.setVisible(True)
        elif "Transkribus" in prov:
            self.lbl_api.setText(self.gm("Transkribus — email:password oppure Bearer token:"))
            self.lbl_custom_model.setVisible(True)
            self.inp_custom_model.setPlaceholderText(self.gm("ID modello HTR (vuoto = 48122, Italian Handwriting M1)"))
            self.inp_custom_model.setVisible(True)
        else:
            self.lbl_api.setText(self.gm("Anthropic API Key:"))
            self.lbl_custom_model.setVisible(True)
            self.inp_custom_model.setVisible(True)

    def load_settings(self):
        try:
            from config_utils import _config_file_path
            import json, os
            cfg = _config_file_path()
            if os.path.exists(cfg):
                with open(cfg, 'r', encoding='utf-8') as f:
                    prefs = json.load(f)
                prov_idx = prefs.get('ocr_provider', 0)
                self.combo_prov.setCurrentIndex(prov_idx)
                # Ripristina tipologia documentale
                saved_type = prefs.get('ocr_doc_type', '')
                if saved_type:
                    idx = self.combo_type.findText(saved_type)
                    if idx >= 0: self.combo_type.setCurrentIndex(idx)

                # Restore memory for textboxes
                self.txt_istruzioni.setText(prefs.get('ocr_custom_prompt', ''))
                self.txt_esempio.setText(prefs.get('ocr_example_text', ''))
                self.inp_custom_model.setText(prefs.get('ocr_custom_model', ''))

                # Restore saved prompts history
                # Restore saved instructions (new dict format via ocr_instructions.json)
                instr_file = self._instructions_file_path()
                if os.path.exists(instr_file):
                    with open(instr_file, 'r', encoding='utf-8') as fi:
                        self.saved_instructions = json.load(fi)
                else:
                    # Migrazione dal vecchio formato lista in config.json
                    old_list = prefs.get('ocr_saved_prompts', [])
                    for i, txt in enumerate(old_list, 1):
                        nome = f"Istruzione {i}"
                        self.saved_instructions[nome] = txt
                    if old_list:
                        self._save_instructions_file()
                self._rebuild_combo_istruzioni()

            # Pre-carica la prima chiave disponibile dalla Cassaforte (KeyManager)
            prov_str = self._current_provider_key()
            try:
                from key_manager import KeyManager, preload_vault_key
                km = KeyManager()
                preloaded = preload_vault_key(prov_str, self.txt_api.text(), km)
                if preloaded != self.txt_api.text().strip():
                    self.txt_api.setText(preloaded)
                    import logging
                    logging.debug("[OCR] Chiave pre-caricata da Cassaforte (%s).", prov_str)
                elif os.path.exists(_config_file_path()):
                    # Fallback: leggi dal config.json
                    with open(_config_file_path(), 'r', encoding='utf-8') as f:
                        self.txt_api.setText(json.load(f).get('ocr_api_key', ''))
            except Exception as km_e:
                import logging
                logging.warning(f"[OCR] Impossibile caricare chiave da Cassaforte: {km_e}")

        except Exception as e:
            import logging
            logging.error(f"Errore caricamento OCR settings: {e}")

    def save_settings(self):
        try:
            from config_utils import _write_config_prefs
            api_testo = self.txt_api.text().strip()
            _write_config_prefs('ocr_api_key', api_testo)
            _write_config_prefs('ocr_provider', self.combo_prov.currentIndex())
            _write_config_prefs('ocr_doc_type', self.combo_type.currentText())
            _write_config_prefs('ocr_custom_prompt', self.txt_istruzioni.toPlainText().strip())
            _write_config_prefs('ocr_example_text', self.txt_esempio.toPlainText().strip())
            _write_config_prefs('ocr_custom_model', self.inp_custom_model.text().strip())
            
            import logging
            logging.debug("[OCR] Impostazioni salvate.")
        except Exception as e:
            import logging
            logging.error(f"Errore salvataggio OCR settings: {e}")

    def start_ocr(self):
        logger.info(f"[AdvancedOCRDialog] Avvio OCR: provider={self.combo_prov.currentText()}, files={self.file_paths}")
        if not self.file_paths:
            QMessageBox.warning(self, self.gm("Attenzione"), self.gm("Seleziona almeno un file."))
            return
        # La chiave può venire dalla Cassaforte (rotazione automatica nel worker)
        # ma se non c'è nemmeno quella nel campo, avvertiamo
        prov_str_check = self._current_provider_key()
        from key_manager import KeyManager
        from config_utils import _config_file_path
        # I provider locali non richiedono chiavi remote.
        if provider_requires_credentials(prov_str_check):
            if not os.path.exists(_config_file_path()) and not KeyManager().has_keys(prov_str_check):
                QMessageBox.warning(
                    self,
                    self.gm("Attenzione"),
                    self.gm(missing_provider_credentials_message(prov_str_check)),
                )
                return
            if not self.txt_api.text().strip() and not KeyManager().has_keys(prov_str_check):
                QMessageBox.warning(
                    self,
                    self.gm("Attenzione"),
                    self.gm(missing_provider_credentials_message(prov_str_check)),
                )
                return

        fmt = []
        if self.chk_txt.isChecked(): fmt.append("txt")
        if self.chk_docx.isChecked(): fmt.append("docx")
        if self.chk_xml.isChecked(): fmt.append("xml")

        if not fmt:
            QMessageBox.warning(self, self.gm("Attenzione"), self.gm("Seleziona almeno un formato di output."))
            return

        self.save_settings()

        out_dir = QFileDialog.getExistingDirectory(self, self.gm("Seleziona cartella di destinazione"))
        if not out_dir: return

        prov_str = self._current_provider_key()

        # Costruisce il prompt dalla tipologia documentale selezionata
        ex_text = self.txt_esempio.toPlainText().strip()
        try:
            final_prompt = self._compose_final_prompt(ex_text)
        except Exception as e:
            import logging, traceback
            logging.error(f"[OCR] Errore composizione prompt: {e}\n{traceback.format_exc()}")
            QMessageBox.critical(
                self,
                self.gm("Errore Prompt"),
                self.gm("Impossibile costruire il prompt OCR:\n{err}").format(err=e),
            )
            return

        self.btn_start.setEnabled(False)
        self.progress_bar.setValue(0)

        # --- Calibrazione Assistita ---
        if self.chk_calibration.isChecked() and not ex_text and self.file_paths:
            try:
                base_prompt = self._compose_final_prompt("")  # prompt senza esempio
            except Exception as e:
                self.btn_start.setEnabled(True)
                return
            self._start_calibration(base_prompt, fmt, out_dir, prov_str)
            return

        # --- Flusso standard ---
        self._launch_ocr_thread(final_prompt, fmt, out_dir, prov_str)

    def _compose_final_prompt(self, ex_text):
        """Compone il prompt finale con il testo di esempio fornito."""
        doc_type = self.combo_type.currentText()
        custom_p = self.txt_istruzioni.toPlainText().strip()
        from ocr_prompts import compose_ocr_prompt
        if self._dtm.is_custom(doc_type):
            custom_ocr = self._dtm.get_ocr_prompt(doc_type) or ""
            return compose_ocr_prompt(
                "Documento Generico / Non Classificato",
                custom_ocr + ("\n" + custom_p if custom_p else ""),
                ex_text
            )
        else:
            override = self._dtm.get_ocr_prompt(doc_type)
            if override:
                prompt = override
                if custom_p:
                    prompt += f"\n\nISTRUZIONI AGGIUNTIVE:\n{custom_p}"
                if ex_text:
                    prompt += f"\n\nTRASCRIZIONE DI ESEMPIO (stessa calligrafia):\n{ex_text}"
                return prompt
            else:
                return compose_ocr_prompt(doc_type, custom_p, ex_text)

    def _launch_ocr_thread(self, final_prompt, fmt, out_dir, prov_str):
        """Avvia il thread OCR principale."""
        interact = self.chk_interactive.isChecked()
        self.thread = OCRThread(
            self.file_paths, prov_str, self.txt_api.text(),
            fmt, out_dir, self.gm("Elaborazione: "),
            final_prompt, "", interact,
            custom_model=self.inp_custom_model.text().strip()
        )
        self.thread.review_requested.connect(self.show_review_dialog)
        self.thread.progress.connect(self.update_progress)
        self.thread.finished.connect(self.ocr_finished)
        self.thread.start()

    def _start_calibration(self, base_prompt, fmt, out_dir, prov_str):
        """Avvia la calibrazione assistita sul primo file del batch."""
        self._calib_fmt      = fmt
        self._calib_out_dir  = out_dir
        self._calib_prov_str = prov_str
        self._calib_base_prompt = base_prompt

        self.progress_lbl.setText(self.gm("Calibrazione: analisi delle prime righe in corso…"))
        self.progress_bar.setMaximum(0)  # indeterminato

        self.calib_thread = CalibrationThread(
            self.file_paths[0], prov_str, self.txt_api.text(), base_prompt
        )
        self.calib_thread.preview_ready.connect(self._on_calibration_ready)
        self.calib_thread.error.connect(self._on_calibration_error)
        self.calib_thread.start()

    def _on_calibration_ready(self, tmp_img_path, raw_text):
        """Mostra il dialog di revisione calibrazione, poi avvia l'elaborazione completa."""
        self.progress_bar.setMaximum(100)
        self.progress_lbl.clear()

        dlg = OCRReviewDialog(
            tmp_img_path, raw_text, self,
            lingua=self.lingua, glossario_data=self.glossario_data,
            ok_label=self.gm("Usa come Riferimento e Continua"),
            skip_label=self.gm("Salta Calibrazione"),
            title=self.gm("Calibrazione Assistita — Correggi le prime righe")
        )

        approved = dlg.exec()
        ex_text = dlg.txt_editor.toPlainText().strip() if approved else ""

        # Pulisci immagine temporanea
        try:
            os.remove(tmp_img_path)
        except Exception:
            pass

        # Se l'utente ha approvato, aggiorna il campo "Trascrizione di Riferimento"
        if approved and ex_text:
            self.txt_esempio.setPlainText(ex_text)

        # Avvia elaborazione completa con o senza esempio
        try:
            final_prompt = self._compose_final_prompt(ex_text)
        except Exception as e:
            import logging, traceback
            logging.error(f"[OCR] Errore composizione prompt post-calibrazione: {e}\n{traceback.format_exc()}")
            QMessageBox.critical(
                self,
                self.gm("Errore Prompt"),
                self.gm("Impossibile costruire il prompt OCR:\n{err}").format(err=e),
            )
            self.btn_start.setEnabled(True)
            return

        self._launch_ocr_thread(final_prompt, self._calib_fmt, self._calib_out_dir, self._calib_prov_str)

    def _on_calibration_error(self, err_msg):
        """Gestisce un errore durante la calibrazione."""
        import logging
        logging.error(f"[OCR] Errore calibrazione: {err_msg}")
        self.btn_start.setEnabled(True)
        self.progress_bar.setMaximum(100)
        self.progress_lbl.clear()
        QMessageBox.critical(self, self.gm("Errore Calibrazione"),
                             f"{self.gm('Errore durante la calibrazione assistita')}:\n{err_msg}")

    def _instructions_file_path(self):
        """Percorso del file JSON delle istruzioni OCR salvate (stessa cartella di genealogy_presets.json)."""
        from config_utils import _EXE_DIR
        import os
        return os.path.join(_EXE_DIR, "ocr_instructions.json")

    def _save_instructions_file(self):
        """Persiste il dizionario saved_instructions su disco."""
        import json
        with open(self._instructions_file_path(), 'w', encoding='utf-8') as f:
            json.dump(self.saved_instructions, f, indent=2, ensure_ascii=False)

    def _rebuild_combo_istruzioni(self):
        """Ricostruisce il combo dalle chiavi del dizionario."""
        self.combo_istruzioni.blockSignals(True)
        self.combo_istruzioni.clear()
        self.combo_istruzioni.addItem(self.gm("-- Istruzioni Salvate --"), "")
        for nome in sorted(self.saved_instructions.keys()):
            self.combo_istruzioni.addItem(nome, self.saved_instructions[nome])
        self.combo_istruzioni.blockSignals(False)

    def load_saved_instruction(self, index):
        if index > 0:
            txt = self.combo_istruzioni.itemData(index)
            self.txt_istruzioni.setText(txt)

    def add_instruction(self):
        """Salva il testo corrente con un nome scelto dall'utente."""
        txt = self.txt_istruzioni.toPlainText().strip()
        if not txt:
            QMessageBox.warning(self, self.gm("Attenzione"), self.gm("Scrivi un'istruzione prima di salvarla."))
            return
        nome, ok = QInputDialog.getText(self, self.gm("Salva Istruzione"), self.gm("Nome per questa istruzione:"))
        if not ok or not nome.strip():
            return
        nome = nome.strip()
        self.saved_instructions[nome] = txt
        self._save_instructions_file()
        self._rebuild_combo_istruzioni()
        idx = self.combo_istruzioni.findText(nome)
        if idx >= 0:
            self.combo_istruzioni.setCurrentIndex(idx)

    def rename_instruction(self):
        """Rinomina l'istruzione selezionata nel combo."""
        idx = self.combo_istruzioni.currentIndex()
        if idx <= 0:
            QMessageBox.warning(self, self.gm("Attenzione"), self.gm("Seleziona prima un'istruzione dal menu."))
            return
        old_nome = self.combo_istruzioni.currentText()
        new_nome, ok = QInputDialog.getText(self, self.gm("Rinomina"), self.gm("Nuovo nome:"), text=old_nome)
        if not ok or not new_nome.strip() or new_nome.strip() == old_nome:
            return
        new_nome = new_nome.strip()
        txt = self.saved_instructions.pop(old_nome)
        self.saved_instructions[new_nome] = txt
        self._save_instructions_file()
        self._rebuild_combo_istruzioni()
        idx = self.combo_istruzioni.findText(new_nome)
        if idx >= 0:
            self.combo_istruzioni.setCurrentIndex(idx)

    def delete_instruction(self):
        """Elimina l'istruzione selezionata nel combo."""
        idx = self.combo_istruzioni.currentIndex()
        if idx <= 0:
            QMessageBox.warning(self, self.gm("Attenzione"), self.gm("Seleziona prima un'istruzione dal menu."))
            return
        nome = self.combo_istruzioni.currentText()
        msg = QMessageBox(self)
        msg.setWindowTitle(self.gm("Elimina Istruzione"))
        msg.setText(f"{self.gm('Rimuovere')} \"{nome}\"?")
        btn_si = msg.addButton(self.gm("Si"), QMessageBox.ButtonRole.YesRole)
        msg.addButton(self.gm("No"), QMessageBox.ButtonRole.NoRole)
        msg.exec()
        if msg.clickedButton() == btn_si:
            self.saved_instructions.pop(nome, None)
            self._save_instructions_file()
            self._rebuild_combo_istruzioni()

    def show_review_dialog(self, img_path, raw_text):
        dlg = OCRReviewDialog(img_path, raw_text, self,
                              lingua=self.lingua, glossario_data=self.glossario_data)
        if dlg.exec():
            # Approva -> salviamo il testo modificato
            self.thread.reviewed_text = dlg.txt_editor.toPlainText().strip()
        else:
            # Salta -> restituiamo None
            self.thread.reviewed_text = None
        self.thread.review_event.set()

    def update_progress(self, val, total, msg):
        self.progress_bar.setMaximum(total)
        self.progress_bar.setValue(val)
        self.progress_lbl.setText(msg)

    def ocr_finished(self, success, msg):
        self.btn_start.setEnabled(True)
        if success:
            QMessageBox.information(self, self.gm("Completato"), self.gm(msg))
        else:
            QMessageBox.critical(self, self.gm("Errore"), self.gm(msg))
