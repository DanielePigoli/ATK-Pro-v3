"""
PromptEditDialog — Permette di visualizzare e sovrascrivere il prompt built-in
di una tipologia documentale per un servizio specifico (OCR / Traduzione / GEDCOM).

Il prompt modificato viene salvato in document_types.json come 'builtin_overrides'.
Il prompt originale è sempre recuperabile con il pulsante "Ripristina Originale".
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QTextEdit, QMessageBox,
)


SERVICE_LABELS = {
    "ocr": "OCR",
    "translation": "Traduzione",
    "gedcom": "GEDCOM",
}


def get_msg(glossario, chiave, lingua):
    try:
        from main_gui_qt import get_msg as _get_msg
        res = _get_msg(glossario, chiave, lingua)
        return res if res is not None else chiave
    except Exception:
        return chiave


class PromptEditDialog(QDialog):
    """
    Aperto dal pulsante ✏ su una tipologia built-in.

    Parametri:
        dtm  (DocumentTypeManager): istanza già caricata
        label (str): etichetta della tipologia (senza prefisso ★)
        service (str): "ocr" | "translation" | "gedcom"
    """

    STYLE = """
        QDialog { background-color: #181818; color: #fff; border: 2px solid #a67c52; }
        QLabel  { color: #f5f0e8; }
        QTextEdit {
            background-color: #2a2a2a; color: #f5f0e8;
            border: 1px solid #555; border-radius: 4px;
            font-family: Consolas, monospace; font-size: 12px;
        }
        QPushButton {
            background-color: #222; color: #fff;
            border: 1px solid #a67c52; padding: 5px 14px; border-radius: 4px;
        }
        QPushButton:hover { background-color: #333; }
        QPushButton#btn_save {
            background-color: #a67c52; border: none; color: #fff; font-weight: bold;
        }
        QPushButton#btn_save:hover { background-color: #c09060; }
        QPushButton#btn_restore {
            background-color: #1a2a1a; border: 1px solid #4a8a4a; color: #88cc88;
        }
        QPushButton#btn_restore:hover { background-color: #223322; }
        QLabel#lbl_override_badge {
            color: #ffaa44; font-size: 11px; font-style: italic;
        }
    """

    def __init__(self, dtm, label: str, service: str, parent=None,
                 lingua: str = "it", glossario_data: dict | None = None):
        super().__init__(parent)
        self._dtm = dtm
        self._label = dtm.bare_label(label)
        self._service = service
        self.lingua = lingua
        self.glossario_data = glossario_data or {}

        has_override = dtm.has_builtin_override(self._label, service)
        svc_name = self._service_name()
        self.setWindowTitle(self._dialog_title(has_override))
        self.setMinimumSize(720, 500)
        self.setStyleSheet(self.STYLE)

        layout = QVBoxLayout(self)
        layout.setSpacing(8)
        layout.setContentsMargins(16, 16, 16, 16)

        # Intestazione
        lbl_info = QLabel(
            f"<b>{self.gm('Tipologia:')}</b> {self._label} &nbsp;|&nbsp; <b>{self.gm('Servizio:')}</b> {svc_name}"
        )
        layout.addWidget(lbl_info)

        if has_override:
            badge = QLabel("⚠ " + self.gm("Override attivo — il prompt originale built-in è stato modificato"))
            badge.setObjectName("lbl_override_badge")
            layout.addWidget(badge)
        else:
            note = QLabel(
                self.gm(
                    "Stai visualizzando il prompt originale built-in. "
                    "Modificalo e salva per creare un override personalizzato."
                )
            )
            note.setWordWrap(True)
            note.setStyleSheet("color: #888; font-size: 11px;")
            layout.addWidget(note)

        if service == "translation":
            note_tr = QLabel(
                "⚠ " + self.gm(
                    "Per la Traduzione il prompt include il testo sorgente dinamicamente. "
                    "Il tuo override verrà usato come sezione 'CONTESTO DOCUMENTO' nel prompt finale."
                )
            )
            note_tr.setWordWrap(True)
            note_tr.setStyleSheet("color: #aa8844; font-size: 11px;")
            layout.addWidget(note_tr)

        # Editor
        self.txt_prompt = QTextEdit()
        self.txt_prompt.setAcceptRichText(False)

        # Carica: se c'è override mostra quello, altrimenti l'originale
        if has_override:
            current = dtm.get_ocr_prompt(self._label) if service == "ocr" else \
                      dtm.get_translation_prompt(self._label) if service == "translation" else \
                      dtm.get_gedcom_prompt(self._label)
            self.txt_prompt.setPlainText(current or "")
        else:
            self.txt_prompt.setPlainText(dtm.get_builtin_original_prompt(self._label, service))

        layout.addWidget(self.txt_prompt, 1)

        # Pulsanti
        btns = QHBoxLayout()
        btn_restore = QPushButton("↩ " + self.gm("Ripristina Originale"))
        btn_restore.setObjectName("btn_restore")
        btn_restore.setToolTip(self.gm("Elimina l'override e torna al prompt built-in originale"))
        btn_restore.clicked.connect(self._restore)

        btn_cancel = QPushButton(self.gm("Annulla"))
        btn_cancel.clicked.connect(self.reject)

        btn_save = QPushButton("✔ " + self.gm("Salva Override"))
        btn_save.setObjectName("btn_save")
        btn_save.clicked.connect(self._save)

        btns.addWidget(btn_restore)
        btns.addStretch()
        btns.addWidget(btn_cancel)
        btns.addWidget(btn_save)
        layout.addLayout(btns)

    def gm(self, chiave):
        return get_msg(self.glossario_data, chiave, self.lingua)

    def _service_name(self):
        return self.gm(SERVICE_LABELS.get(self._service, self._service.upper()))

    def _dialog_title(self, has_override=False):
        marker = f" ★ {self.gm('Override attivo')}" if has_override else ""
        return f"{self.gm('Prompt')} {self._service_name()} — {self._label}{marker}"

    def _save(self):
        text = self.txt_prompt.toPlainText().strip()
        if not text:
            QMessageBox.warning(
                self,
                self.gm("Attenzione"),
                self.gm(
                    "Il prompt non può essere vuoto. "
                    "Usa 'Ripristina Originale' per tornare al default."
                ),
            )
            return
        self._dtm.set_builtin_override(self._label, self._service, text)
        self.accept()

    def _restore(self):
        msg = QMessageBox(self)
        msg.setWindowTitle(self.gm("Ripristina Originale"))
        msg.setText(
            self.gm(
                "Eliminare l'override per «{label}» ({service})?\n"
                "Verrà ripristinato il prompt built-in originale."
            ).format(label=self._label, service=self._service_name())
        )
        btn_si = msg.addButton(self.gm("Sì, ripristina"), QMessageBox.ButtonRole.YesRole)
        msg.addButton(self.gm("Annulla"), QMessageBox.ButtonRole.NoRole)
        msg.exec()
        if msg.clickedButton() == btn_si:
            self._dtm.delete_builtin_override(self._label, self._service)
            # Mostra il prompt originale nell'editor
            self.txt_prompt.setPlainText(
                self._dtm.get_builtin_original_prompt(self._label, self._service)
            )
            self.setWindowTitle(self._dialog_title(False))
            QMessageBox.information(
                self,
                self.gm("Ripristinato"),
                self.gm("Override eliminato. Il prompt built-in originale è ripristinato."),
            )
