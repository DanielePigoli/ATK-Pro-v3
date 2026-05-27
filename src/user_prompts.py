import os as _os
import sys as _sys
# Calcola percorso assoluto base (funziona sia in sviluppo sia da PyInstaller --onedir)
_UP_BASE = getattr(_sys, '_MEIPASS', _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))))
def _ico():
    return _os.path.join(_UP_BASE, "assets", "common", "grafici", "ATK-Pro.ico")


def ask_generate_pdf_missing_images(missing_count, glossario_data=None, lingua="IT", parent=None, dark_mode=False):
    """
    Mostra una finestra di dialogo localizzata che avvisa l’utente che mancano N immagini e chiede se generare comunque il PDF.
    Restituisce True se l'utente conferma, False altrimenti.
    """
    import threading
    prefer_qt = parent is not None
    timeout_sec = 30
    msg_default = f"Mancano {missing_count} immagini. Vuoi generare comunque il PDF?"
    si_text = "Sì"
    no_text = "No"
    title_text = "PDF incompleto"
    if glossario_data is not None:
        try:
            from main_gui_qt import get_msg
            msg_default = get_msg(glossario_data, "Mancano alcune immagini. Vuoi generare comunque il PDF?", lingua.upper()).replace("{N}", str(missing_count))
            si_text = get_msg(glossario_data, "Si", lingua.upper())
            no_text = get_msg(glossario_data, "No", lingua.upper())
            title_text = get_msg(glossario_data, "PDF incompleto", lingua.upper()) or "PDF incompleto"
        except Exception:
            pass
    if prefer_qt:
        try:
            from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton
            from PySide6.QtGui import QIcon
            from PySide6.QtCore import Qt, QTimer
            from main_gui_qt import _setup_dialog_pergamena
            dlg = QDialog(parent) if parent is not None else QDialog()
            dlg.resize(420, 170)
            dlg.setWindowTitle(title_text)
            try:
                dlg.setWindowIcon(QIcon(_ico()))
            except Exception:
                pass
            try:
                _setup_dialog_pergamena(dlg, 420, 170)
            except Exception:
                pass
            if dark_mode:
                dlg.setStyleSheet("QDialog { background-color: #181818; border: 2px solid #a67c52; } QLabel, QPushButton { color: #fff; font-size: 15px; } QPushButton { background-color: #222; border: 1px solid #a67c52; padding: 8px 24px; border-radius: 8px; font-weight: bold; } QPushButton:hover { background-color: #333; }")
            else:
                dlg.setStyleSheet("QDialog { background: #fff; border: 2px solid #a67c52; } QLabel, QPushButton { color: #482e1a; font-size: 15px; } QPushButton { background-color: #d2bb8a; border: 1px solid #a67c52; padding: 8px 24px; border-radius: 8px; font-weight: bold; } QPushButton:hover { background-color: #e5d3b3; }")
            layout = QVBoxLayout(dlg)
            label = QLabel(msg_default)
            label.setAlignment(Qt.AlignCenter)
            label.setWordWrap(True)
            if dark_mode:
                label.setStyleSheet("color: #fff; font-size: 16px; font-weight: bold; background: transparent;")
            layout.addWidget(label)
            btn_frame = QHBoxLayout()
            si_btn = QPushButton(si_text)
            no_btn = QPushButton(no_text)
            si_btn.clicked.connect(dlg.accept)
            no_btn.clicked.connect(dlg.reject)
            btn_frame.addWidget(si_btn)
            btn_frame.addWidget(no_btn)
            layout.addLayout(btn_frame)
            try:
                dlg.setWindowModality(Qt.ApplicationModal)
            except Exception:
                pass
            try:
                from PySide6.QtGui import QGuiApplication
                screen = QGuiApplication.primaryScreen()
                if screen is not None:
                    available = screen.availableGeometry()
                    try:
                        dlg.adjustSize()
                    except Exception:
                        pass
                    dlg_geo = dlg.frameGeometry()
                    dlg_geo.moveCenter(available.center())
                    dlg.move(dlg_geo.topLeft())
            except Exception:
                pass
            # Timeout automatico
            result = {'val': None}
            def auto_accept():
                if result['val'] is None:
                    result['val'] = True
                    dlg.accept()
            timer = QTimer(dlg)
            timer.setSingleShot(True)
            timer.timeout.connect(auto_accept)
            timer.start(timeout_sec * 1000)
            accepted = dlg.exec() == QDialog.Accepted
            if result['val'] is None:
                result['val'] = accepted
            return bool(result['val']) is True
        except Exception:
            prefer_qt = False
    # Fallback: tkinter
    if not prefer_qt:
        try:
            import tkinter as tk
            import threading
            root = tk.Tk()
            root.title("PDF incompleto")
            selected = {'val': None}
            def on_si():
                selected['val'] = True
                try:
                    root.quit()
                except Exception:
                    pass
            def on_no():
                selected['val'] = False
                try:
                    root.quit()
                except Exception:
                    pass
            lbl = tk.Label(root, text=msg_default)
            lbl.pack(pady=10)
            btn_frame = tk.Frame(root)
            btn_frame.pack(pady=10)
            tk.Button(btn_frame, text=si_text, command=on_si).pack(side='left', padx=10)
            tk.Button(btn_frame, text=no_text, command=on_no).pack(side='right', padx=10)
            def auto_accept():
                if selected['val'] is None:
                    selected['val'] = True
                    try:
                        root.quit()
                    except Exception:
                        pass
            timer = threading.Timer(timeout_sec, auto_accept)
            timer.start()
            try:
                root.mainloop()
            except Exception:
                pass
            timer.cancel()
            try:
                root.destroy()
            except Exception:
                pass
            return bool(selected['val']) is True
        except Exception:
            return False
# === Copertura test ===
# ✔ Test realistici presenti
# ✔ Rami difensivi simulati
# ✅ Validato (logico)

# === Copertura test ===
# tests/test_user_prompts.py → selezione formati immagine, conferma/annulla GUI, generazione PDF, chiusura finestra
# ✅ Validato (logico) — test attivi e rami difensivi verificati

import os
import logging
import sys

logger = logging.getLogger(__name__)
try:
    import tkinter as tk
except ImportError:
    tk = None


def ask_image_formats(glossario_data=None, lingua="IT", format_vars=None):
    """
    Mostra una finestra di dialogo per selezionare i formati immagine desiderati.
    Restituisce una lista di estensioni selezionate (es. ['jpg', 'png']).
    Se la GUI non è disponibile, chiede in console.
    Supporta localizzazione tramite glossario_data.
    """
    # Helper per localizzazione
    def get_msg_fallback(key, fallback):
        if glossario_data is None:
            return fallback
        try:
            from metadata_utils import get_msg
            return get_msg(glossario_data, key, lingua.upper())
        except Exception:
            return fallback

    # Caso test/mock: uso diretto senza GUI
    if format_vars is not None:
        return [fmt.lower() for fmt, var in format_vars.items() if var.get()]

    try:
        global tk
        if tk is None:
            import tkinter as tk
        # Caso normale: GUI interattiva
        selected_formats = []

        def conferma():
            nonlocal selected_formats
            selected_formats = [fmt.lower() for fmt, var in format_vars.items() if var.get()]
            root.quit()

        root = tk.Tk()
        root.title(get_msg_fallback("Seleziona formati immagine", "Seleziona formati immagine"))
        tk.Label(root, text=get_msg_fallback("Scegli i formati immagine da generare", "Scegli i formati immagine da generare:")).pack(pady=10)

        format_options = ["JPG", "PNG", "TIFF"]
        format_vars = {}
        for fmt in format_options:
            var = tk.BooleanVar()
            tk.Checkbutton(root, text=fmt, variable=var).pack(anchor='w', padx=20)
            format_vars[fmt] = var

        tk.Frame(root, height=1, bg='gray').pack(fill='x', padx=10, pady=4)
        tk.Label(root, text=get_msg_fallback("Documento PDF", "Documento PDF:"), font=('TkDefaultFont', 9, 'bold')).pack(anchor='w', padx=10)
        var_pdf = tk.BooleanVar()
        tk.Checkbutton(root, text="PDF", variable=var_pdf).pack(anchor='w', padx=20)
        format_vars["PDF"] = var_pdf

        btn_frame = tk.Frame(root)
        btn_frame.pack(pady=10)
        tk.Button(btn_frame, text=get_msg_fallback("Conferma", "Conferma"), command=conferma).pack(side='left', padx=10)
        tk.Button(btn_frame, text=get_msg_fallback("Annulla", "Annulla"), command=root.quit).pack(side='right', padx=10)

        root.mainloop()
        root.destroy()
        return selected_formats

    except Exception:
        # Fallback console
        console_msg = get_msg_fallback("Scegli i formati immagine da generare", "Formati immagine da generare (separa con virgola, es. jpg,png,tiff):")
        scelta = input(f"{console_msg} ").strip().lower()
        return [s.strip() for s in scelta.split(",") if s.strip()]


def ask_generate_pdf(glossario_data=None, lingua="IT", parent=None, dark_mode=False):
    """
    Mostra una finestra di dialogo PySide6 per chiedere se generare il PDF completo del registro.
    Restituisce True se l'utente conferma, False altrimenti.
    Se la GUI non è disponibile, chiede in console.
    """
    # Se il caller fornisce un `parent` (es. la MainWindow Qt), usiamo PySide6
    # per mantenere lo stile e la centratura corretta; altrimenti preferiamo
    # tkinter come fallback per i test che lo mockano.
    import threading
    prefer_qt = parent is not None
    timeout_sec = 30

    if prefer_qt:
        try:
            from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton
            from PySide6.QtGui import QIcon
            from PySide6.QtCore import Qt, QTimer
            from main_gui_qt import get_msg, _setup_dialog_pergamena
            import os

            dlg = QDialog(parent) if parent is not None else QDialog()
            dlg.resize(400, 150)

            title_key = "Generazione PDF" if glossario_data is None else get_msg(glossario_data, "Generazione PDF", lingua.upper())
            dlg.setWindowTitle(title_key)
            try:
                dlg.setWindowIcon(QIcon(_ico()))
            except Exception:
                pass
            try:
                _setup_dialog_pergamena(dlg, 400, 150)
            except Exception:
                pass
            # STILE UNIFICATO: chiaro o scuro
            if dark_mode:
                dlg.setStyleSheet("QDialog { background-color: #181818; border: 2px solid #a67c52; } QLabel, QPushButton { color: #fff; font-size: 15px; } QPushButton { background-color: #222; border: 1px solid #a67c52; padding: 8px 24px; border-radius: 8px; font-weight: bold; } QPushButton:hover { background-color: #333; }")
            else:
                dlg.setStyleSheet("QDialog { background: #fff; border: 2px solid #a67c52; } QLabel, QPushButton { color: #482e1a; font-size: 15px; } QPushButton { background-color: #d2bb8a; border: 1px solid #a67c52; padding: 8px 24px; border-radius: 8px; font-weight: bold; } QPushButton:hover { background-color: #e5d3b3; }")

            layout = QVBoxLayout(dlg)
            # Testo generico valido per documenti e registri
            text_key = "Vuoi generare il PDF completo?" if glossario_data is None else get_msg(glossario_data, "Vuoi generare il PDF completo?", lingua.upper())
            label = QLabel(text_key)
            label.setAlignment(Qt.AlignCenter)
            label.setWordWrap(True)
            if dark_mode:
                label.setStyleSheet("color: #fff; font-size: 16px; font-weight: bold; background: transparent;")
            layout.addWidget(label)

            btn_frame = QHBoxLayout()
            si_text = "Sì" if glossario_data is None else get_msg(glossario_data, "Si", lingua.upper())
            no_text = "No" if glossario_data is None else get_msg(glossario_data, "No", lingua.upper())
            si_btn = QPushButton(si_text)
            no_btn = QPushButton(no_text)
            si_btn.clicked.connect(dlg.accept)
            no_btn.clicked.connect(dlg.reject)
            btn_frame.addWidget(si_btn)
            btn_frame.addWidget(no_btn)
            layout.addLayout(btn_frame)

            try:
                dlg.setWindowModality(Qt.ApplicationModal)
            except Exception:
                pass
            try:
                from PySide6.QtGui import QGuiApplication
                screen = QGuiApplication.primaryScreen()
                if screen is not None:
                    available = screen.availableGeometry()
                    try:
                        dlg.adjustSize()
                    except Exception:
                        pass
                    dlg_geo = dlg.frameGeometry()
                    dlg_geo.moveCenter(available.center())
                    dlg.move(dlg_geo.topLeft())
            except Exception:
                pass
            # Timeout automatico
            result = {'val': None}
            def auto_accept():
                if result['val'] is None:
                    result['val'] = True
                    dlg.accept()
            timer = QTimer(dlg)
            timer.setSingleShot(True)
            timer.timeout.connect(auto_accept)
            timer.start(timeout_sec * 1000)
            accepted = dlg.exec() == QDialog.Accepted
            if result['val'] is None:
                result['val'] = accepted
            return bool(result['val']) is True
        except Exception:
            prefer_qt = False

    if not prefer_qt:
        try:
            import tkinter as tk
            import threading
            try:
                from main_gui_qt import get_msg as _gm_tk
            except Exception:
                _gm_tk = lambda g, k, l: None
            root = tk.Tk()
            _title_tk = (_gm_tk(glossario_data, "Generazione PDF", lingua.upper()) if glossario_data else None) or "Generazione PDF"
            root.title(_title_tk)
            selected = {'val': None}

            def on_si():
                selected['val'] = True
                try:
                    root.quit()
                except Exception:
                    pass

            def on_no():
                selected['val'] = False
                try:
                    root.quit()
                except Exception:
                    pass

            _q_tk = (_gm_tk(glossario_data, "Vuoi generare il PDF completo?", lingua.upper()) if glossario_data else None) or "Vuoi generare il PDF completo del registro?"
            lbl = tk.Label(root, text=_q_tk)
            lbl.pack(pady=10)
            btn_frame = tk.Frame(root)
            btn_frame.pack(pady=10)
            _si_tk = (_gm_tk(glossario_data, "Si", lingua.upper()) if glossario_data else None) or "Sì"
            _no_tk = (_gm_tk(glossario_data, "No", lingua.upper()) if glossario_data else None) or "No"
            tk.Button(btn_frame, text=_si_tk, command=on_si).pack(side='left', padx=10)
            tk.Button(btn_frame, text=_no_tk, command=on_no).pack(side='right', padx=10)

            def auto_accept():
                if selected['val'] is None:
                    selected['val'] = True
                    try:
                        root.quit()
                    except Exception:
                        pass
            timer = threading.Timer(timeout_sec, auto_accept)
            timer.start()
            try:
                root.mainloop()
            except Exception:
                pass
            timer.cancel()
            try:
                root.destroy()
            except Exception:
                pass

            # Se l'utente ha chiuso la finestra senza scelta, consideriamo Sì
            return bool(selected['val']) is True

        except Exception:
            # Fallback console se nessuna GUI disponibile
            try:
                from main_gui_qt import get_msg as _gm_c
                _prompt_c = (_gm_c(glossario_data, "Vuoi generare il PDF completo?", lingua.upper()) if glossario_data else None) or "Vuoi generare il PDF completo del registro?"
                _prompt_c = _prompt_c.rstrip() + " (s/n): "
            except Exception:
                _prompt_c = "Vuoi generare anche il PDF completo del registro? (s/n): "
            scelta = input(_prompt_c).strip().lower()
            return scelta == "s"


class ProgressDialog:
    """Dialog Qt per mostrare progresso in tempo reale durante l'elaborazione.

    Uso:
      pd = ProgressDialog(glossario_data, lingua, total=4)
      pd.show()
      pd.update(current=1, name='Registro 1')
      ... chiamare QCoreApplication.processEvents() nel loop per mantenere UI reattiva
      if pd.cancelled: interrompere elaborazione
    """
    def __init__(self, glossario_data=None, lingua="IT", total: int = 1, parent=None):
        self.glossario = glossario_data
        self.lingua = lingua
        self.total = max(1, int(total))
        self.parent = parent
        self.cancelled = False
        # Tentativo di import PySide6
        try:
            from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QProgressBar, QPushButton, QHBoxLayout
            from PySide6.QtCore import Qt
            from PySide6.QtGui import QIcon, QFont
            from main_gui_qt import _setup_dialog_pergamena, get_msg

            self._use_qt = True
            # Crea il dialog con parent se fornito per ereditare stile e proprietà
            self.dialog = QDialog(parent) if parent is not None else QDialog()
            # La finestra sarà sopra la MainWindow se parent è fornito, ma non sempre in primo piano
            # Rimosso WindowStaysOnTopHint: la finestra non sarà prepotente, ma solo sopra la GUI principale
            # Titolo e icona localizzati
            # Conserva il riferimento alla funzione di localizzazione per
            # poterla usare anche in `update` (import fatta qui per evitare
            # dipendenze circolari all'importazione del modulo).
            self._get_msg = get_msg
            title_txt = self._get_msg(self.glossario, "Elaborazione in corso", self.lingua.upper()) if self.glossario else "Elaborazione in corso"
            self.dialog.setWindowTitle(title_txt)
            try:
                from main_gui_qt import asset_path
                ico_path = asset_path("assets/common/grafici/ATK-Pro.ico")
                if not os.path.exists(ico_path):
                    ico_path = asset_path("assets/common/grafici/ATK-Pro-64.png")
                self.dialog.setWindowIcon(QIcon(ico_path))
            except Exception:
                pass
            _setup_dialog_pergamena(self.dialog, 480, 160)
            # Modalità applicativa per coerenza con altri dialog
            try:
                self.dialog.setWindowModality(Qt.ApplicationModal)
            except Exception:
                pass

            layout = QVBoxLayout(self.dialog)
            # Etichetta iniziale formattata (usa la funzione di localizzazione
            # memorizzata in `self._get_msg` per evitare NameError in `update`).
            try:
                if self.glossario:
                    label_txt = self._get_msg(self.glossario, "Elaborazione record: {n}/{tot}", self.lingua.upper()).format(n=0, tot=self.total)
                else:
                    label_txt = "Elaborazione record: 0/{}".format(self.total)
            except Exception:
                label_txt = "Elaborazione record: 0/{}".format(self.total)
            self.label = QLabel(label_txt)
            self.label.setAlignment(Qt.AlignCenter)
            f = QFont()
            f.setPointSize(12)
            f.setBold(True)
            self.label.setFont(f)
            self.label.setStyleSheet("color: #fff; background: transparent; font-size: 16px; font-weight: bold;")
            layout.addWidget(self.label)

            pbar_layout = QHBoxLayout()
            self.pbar = QProgressBar()
            self.pbar.setMinimum(0)
            self.pbar.setMaximum(self.total)
            self.pbar.setTextVisible(False)
            self.pbar.setStyleSheet("QProgressBar { background: #222; color: #fff; border: 1px solid #a67c52; border-radius: 6px; height: 18px; } QProgressBar::chunk { background: #a67c52; }")
            pbar_layout.addWidget(self.pbar)
            self.n_label = QLabel(f"0/{self.total}")
            self.n_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.n_label.setStyleSheet("color: #fff; font-size: 15px; font-weight: bold; min-width: 70px; background: transparent;")
            pbar_layout.addWidget(self.n_label)
            layout.addLayout(pbar_layout)

            btns = QHBoxLayout()
            cancel_txt = self._get_msg(self.glossario, "Annulla", self.lingua.upper()) if self.glossario else "Annulla"
            if not cancel_txt or cancel_txt == 'None':
                cancel_txt = "Annulla"
            self.cancel_btn = QPushButton(cancel_txt)
            self.cancel_btn.setStyleSheet("background-color: #222; color: #fff; border: 1px solid #a67c52; padding: 8px 24px; border-radius: 8px; font-size: 15px; font-weight: bold;")
            self.cancel_btn.clicked.connect(self._on_cancel)
            btns.addStretch()
            btns.addWidget(self.cancel_btn)
            layout.addLayout(btns)
            # Centra il dialogo sullo schermo dopo la costruzione
            try:
                self.center_on_screen()
            except Exception:
                pass

        except Exception:
            # PySide6 non disponibile -> fallback console
            self._use_qt = False
            self.dialog = None

    def _on_cancel(self):
        self.cancelled = True
        try:
            self.dialog.reject()
        except Exception:
            pass

    def center_on_screen(self):
        """Centra il dialogo sulla schermata primaria disponibile."""
        try:
            # Import locale per evitare dipendenze all'import del modulo
            from PySide6.QtGui import QGuiApplication
            screen = QGuiApplication.primaryScreen()
            if screen is None:
                return
            available = screen.availableGeometry()
            dlg_geo = self.dialog.frameGeometry()
            dlg_geo.moveCenter(available.center())
            self.dialog.move(dlg_geo.topLeft())
        except Exception:
            # In caso di qualsiasi problema, non blocchiamo l'esecuzione
            return

    def show(self):
        if self._use_qt and self.dialog:
            try:
                # Assicura centratura aggiornata e mostra in modo non bloccante
                try:
                    self.center_on_screen()
                except Exception:
                    pass
                self.dialog.show()
                try:
                    self.dialog.setFocus()
                except Exception:
                    pass
                try:
                    self.dialog.raise_()
                    self.dialog.activateWindow()
                except Exception:
                    pass
                # Dopo la mostra, la dimensione potrebbe cambiare a seguito di layout/wordwrap;
                # rimettiamo a posto la centratura appena possibile.
                try:
                    from PySide6.QtCore import QTimer
                    QTimer.singleShot(0, self.center_on_screen)
                except Exception:
                    try:
                        self.center_on_screen()
                    except Exception:
                        pass
            except Exception:
                pass

    def close(self):
        if self._use_qt and self.dialog:
            try:
                self.dialog.close()
            except Exception:
                pass

    def update(self, current: int, name: str = None, page: int = None, page_total: int = None):
        # Aggiorna la barra e la label
        cur = int(current)
        if self._use_qt and self.dialog:
            try:
                # Aggiorna barra di progresso (valore numerico)
                self.pbar.setValue(min(cur, self.total))
                # Testo principale: Record n/N — nome — pag. x/y (mai solo pag. x)
                _rec_tmpl = self._get_msg(self.glossario, "Record {n}/{tot}", self.lingua.upper()) if self.glossario else None
                _rec_tmpl = _rec_tmpl or "Record {n}/{tot}"
                n_text = _rec_tmpl.format(n=cur, tot=self.total)
                import re
                if name:
                    name = re.sub(r'—?\s*pag\.\s*\d+\s*$', '', name).strip()
                    n_text += f" — {name}"
                if page is not None and page_total is not None and page_total > 0:
                    _pag = self._get_msg(self.glossario, "pag.", self.lingua.upper()) if self.glossario else None
                    _pag = _pag or "pag."
                    n_text += f" — {_pag} {page}/{page_total}"
                self.label.setText(n_text)
                self.n_label.setText(f"{cur}/{self.total}")
                logger.debug(f"[ProgressDialog] update: cur={cur} total={self.total} name={name} text='{n_text}'")
                try:
                    self.dialog.adjustSize()
                except Exception:
                    pass
                try:
                    self.center_on_screen()
                except Exception:
                    pass
                try:
                    self.dialog.raise_()
                    self.dialog.activateWindow()
                except Exception:
                    pass
            except Exception:
                pass
        else:
            # Console fallback: stampa semplice
            line = f"[{cur}/{self.total}] {name or ''}"
            if page is not None and page_total is not None:
                line += f" | pag. {page}/{page_total} salvate"
            try:
                print(line)
            except Exception:
                pass


def show_error(message, glossario_data=None, lingua="IT", parent=None, level="error", log_only=False):
    """
    Mostra un messaggio di errore/warning/info all'utente (QMessageBox se GUI, altrimenti console), sempre loggando.
    level: "error", "warning", "info"
    log_only: se True, non mostra dialogo ma solo logga
    """
    logger = logging.getLogger(__name__)
    # Localizzazione messaggio se glossario disponibile
    msg = message
    if glossario_data is not None:
        try:
            from main_gui_qt import get_msg
            loc = get_msg(glossario_data, message, lingua.upper())
            if loc:
                msg = loc
        except Exception:
            pass
    # Logging
    if level == "error":
        logger.error(msg)
    elif level == "warning":
        logger.warning(msg)
    else:
        logger.info(msg)
    if log_only:
        return
    # Mostra dialogo se GUI disponibile
    try:
        from PySide6.QtWidgets import QMessageBox
        icon = QMessageBox.Critical if level == "error" else (QMessageBox.Warning if level == "warning" else QMessageBox.Information)
        box = QMessageBox(parent) if parent is not None else QMessageBox()
        box.setIcon(icon)
        box.setWindowTitle({"error": "Errore", "warning": "Attenzione", "info": "Info"}[level])
        box.setText(msg)
        box.setStandardButtons(QMessageBox.Ok)
        box.exec()
    except Exception:
        # Fallback console
        print(f"[{level.upper()}] {msg}", file=sys.stderr if level=="error" else sys.stdout)
