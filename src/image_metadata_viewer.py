"""
image_metadata_viewer.py – Visualizzatori immagini e metadati JSON per ATK-Pro.

Fornisce due funzioni principali:
  - apri_visualizzatore_immagini():  apre un file immagine (JPG/PNG/TIFF) con
    anteprima e, se presente, il sidecar JSON affiancato.
  - apri_visualizzatore_metadati():  apre un file JSON sidecar con i metadati
    e, se presente, l'immagine abbinata affiancata.
"""

from __future__ import annotations

import json
import os
from io import BytesIO

from PySide6.QtCore import Qt, QPoint
from PySide6.QtGui import QIcon, QImage, QPixmap, QWheelEvent
from PySide6.QtWidgets import (
    QDialog, QFileDialog, QHBoxLayout, QLabel, QMessageBox,
    QPushButton, QScrollArea, QSizePolicy, QSpinBox,
    QSplitter, QTreeWidget, QTreeWidgetItem, QVBoxLayout, QWidget,
)


# ---------------------------------------------------------------------------
# Helper localizzazione: get_msg con fallback IT
# ---------------------------------------------------------------------------
def _gm(glossario_data, key: str, lingua: str) -> str:
    """Chiama get_msg con fallback case-insensitive e poi alla chiave raw."""
    try:
        try:
            from main_gui_qt import get_msg  # type: ignore
        except ImportError:
            from src.main_gui_qt import get_msg  # type: ignore
        # 1) Tentativo esatto
        result = get_msg(glossario_data, key, lingua)
        if result:
            return result
        # 2) Tentativo title-case (es. "datazione" → "Datazione")
        result = get_msg(glossario_data, key.title(), lingua)
        if result:
            return result
        # 3) Tentativo capitalize (es. "contesto archivistico" → "Contesto archivistico")
        result = get_msg(glossario_data, key.capitalize(), lingua)
        if result:
            return result
        # 4) Tentativo lowercase (es. "Titolo" → "titolo")
        result = get_msg(glossario_data, key.lower(), lingua)
        if result:
            return result
    except Exception:
        pass
    return key

# ---------------------------------------------------------------------------
# Stile condiviso (dark-theme coerente con il resto dell'app)
# ---------------------------------------------------------------------------
_DARK_STYLE = """
QDialog {
    background-color: #181818;
    color: #fff;
}
QWidget {
    background-color: #181818;
    color: #fff;
}
QSplitter::handle {
    background-color: #a67c52;
    width: 2px;
}
QTreeWidget {
    background-color: #1e1e1e;
    color: #fff;
    border: 1px solid #a67c52;
    alternate-background-color: #222;
    gridline-color: #333;
    font-size: 13px;
}
QTreeWidget::item:selected {
    background-color: #a67c52;
    color: #000;
}
QHeaderView::section {
    background-color: #2a2a2a;
    color: #a67c52;
    border: 1px solid #a67c52;
    padding: 8px 10px;
    font-weight: bold;
    font-size: 13px;
    height: 44px;
}
QScrollArea {
    border: 1px solid #a67c52;
    background-color: #111;
}
QLabel#img_label {
    background-color: #111;
}
QPushButton, QToolButton {
    background-color: #222;
    color: #fff;
    border: 1px solid #a67c52;
    padding: 6px 14px;
    border-radius: 6px;
    font-weight: bold;
    font-size: 13px;
    min-width: 36px;
    min-height: 28px;
}
QPushButton:hover, QToolButton:hover {
    background-color: #333;
}
QSpinBox {
    background-color: #222;
    color: #fff;
    border: 1px solid #a67c52;
    padding: 2px 6px;
    border-radius: 4px;
    font-size: 13px;
}
QLabel {
    color: #fff;
    font-size: 13px;
}
"""


# ---------------------------------------------------------------------------
# Utility: carica un'immagine via Pillow → QPixmap
# ---------------------------------------------------------------------------
def _pil_to_qpixmap(pil_img) -> QPixmap:
    """Converte un frame PIL (qualsiasi mode) in QPixmap."""
    buf = BytesIO()
    pil_img.save(buf, format="PNG")
    buf.seek(0)
    qimg = QImage.fromData(buf.read())
    return QPixmap.fromImage(qimg)


def _load_pil(path: str):
    """Ritorna un'istanza PIL.Image o None se non disponibile."""
    try:
        from PIL import Image  # type: ignore
        return Image.open(path)
    except Exception:
        return None


def _find_image_for_json(json_path: str) -> str | None:
    """Cerca il file immagine abbinato al sidecar JSON (stesso nome, ext diversa)."""
    base = os.path.splitext(json_path)[0]
    for ext in (".jpg", ".jpeg", ".png", ".tif", ".tiff"):
        candidate = base + ext
        if os.path.exists(candidate):
            return candidate
    return None


def _find_json_for_image(img_path: str) -> str | None:
    """Cerca il sidecar JSON abbinato a un file immagine."""
    base = os.path.splitext(img_path)[0]
    candidate = base + ".json"
    return candidate if os.path.exists(candidate) else None


# ---------------------------------------------------------------------------
# Widget pannello immagine riutilizzabile (con zoom e scorrimento)
# ---------------------------------------------------------------------------
class _ZoomScrollArea(QScrollArea):
    """ScrollArea con zoom a rotella e pan a trascinamento."""

    def __init__(self, on_wheel, parent=None):
        super().__init__(parent)
        self._on_wheel = on_wheel
        self._drag_pos = None

    def wheelEvent(self, event: QWheelEvent):
        # Rotella → zoom sempre (nessun modificatore richiesto)
        self._on_wheel(event.angleDelta().y())
        event.accept()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._drag_pos = event.position().toPoint()
            self.setCursor(Qt.ClosedHandCursor)
            event.accept()
        else:
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self._drag_pos is not None and (event.buttons() & Qt.LeftButton):
            delta = event.position().toPoint() - self._drag_pos
            self._drag_pos = event.position().toPoint()
            self.horizontalScrollBar().setValue(
                self.horizontalScrollBar().value() - delta.x()
            )
            self.verticalScrollBar().setValue(
                self.verticalScrollBar().value() - delta.y()
            )
            event.accept()
        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._drag_pos = None
            self.setCursor(Qt.ArrowCursor)
            event.accept()
        else:
            super().mouseReleaseEvent(event)

    def enterEvent(self, event):
        self.setCursor(Qt.OpenHandCursor)
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.setCursor(Qt.ArrowCursor)
        super().leaveEvent(event)


class _ImagePanel(QWidget):
    """Pannello con scroll, zoom interattivo e supporto TIFF multi-pagina."""

    _ZOOM_STEP = 0.15
    _ZOOM_MIN  = 0.05
    _ZOOM_MAX  = 8.0

    def __init__(self, pil_img=None, n_pages: int = 1, parent=None,
                 glossario_data=None, lingua: str = "IT"):
        super().__init__(parent)
        self._pil_img   = pil_img
        self._n_pages   = n_pages
        self._zoom      = 1.0
        self._base_pix  = None
        self._fit_mode  = True
        gd, lg = glossario_data, lingua
        self._glossario_data = gd
        self._lingua = lg

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)

        # --- Barra controlli zoom ---
        ctrl_row = QHBoxLayout()
        ctrl_row.setContentsMargins(4, 2, 4, 2)
        ctrl_row.setSpacing(4)

        self._btn_zoom_out = QPushButton("  −  ")
        self._btn_zoom_out.setToolTip(_gm(gd, "Riduci", lg) + " (↓)")
        self._btn_zoom_out.setMinimumWidth(44)
        self._btn_zoom_out.clicked.connect(self._zoom_out)

        self._lbl_zoom = QLabel("100%")
        self._lbl_zoom.setMinimumWidth(58)
        self._lbl_zoom.setAlignment(Qt.AlignCenter)
        self._lbl_zoom.setStyleSheet(
            "color: #a67c52; font-weight: bold; font-size: 13px;"
            "background: #1a1a1a; border: 1px solid #444;"
            "border-radius: 4px; padding: 2px 4px;"
        )

        self._btn_zoom_in = QPushButton("  +  ")
        self._btn_zoom_in.setToolTip(_gm(gd, "Ingrandisci", lg) + " (↑)")
        self._btn_zoom_in.setMinimumWidth(44)
        self._btn_zoom_in.clicked.connect(self._zoom_in)

        self._btn_fit = QPushButton(" " + _gm(gd, "Adatta alla finestra", lg) + " ")
        self._btn_fit.setToolTip(_gm(gd, "Adatta alla finestra", lg))
        self._btn_fit.setMinimumWidth(80)
        self._btn_fit.clicked.connect(self._fit_to_view)

        self._btn_orig = QPushButton(" 1:1 ")
        self._btn_orig.setToolTip(_gm(gd, "Dimensione originale", lg))
        self._btn_orig.setMinimumWidth(52)
        self._btn_orig.clicked.connect(self._zoom_1to1)

        lbl_hint = QLabel("🖱 " + _gm(gd, "Trascina per spostare", lg))
        lbl_hint.setStyleSheet("color: #666; font-size: 11px;")

        ctrl_row.addWidget(self._btn_zoom_out)
        ctrl_row.addWidget(self._lbl_zoom)
        ctrl_row.addWidget(self._btn_zoom_in)
        ctrl_row.addSpacing(8)
        ctrl_row.addWidget(self._btn_fit)
        ctrl_row.addWidget(self._btn_orig)
        ctrl_row.addSpacing(12)
        ctrl_row.addWidget(lbl_hint)
        ctrl_row.addStretch()

        # Controlli pagina (solo TIFF multi-pagina)
        if n_pages > 1:
            ctrl_row.addWidget(QLabel(_gm(gd, "Pagina", lg) + ":"))
            self._spin = QSpinBox()
            self._spin.setRange(1, n_pages)
            self._spin.setValue(1)
            self._spin.setFixedWidth(60)
            ctrl_row.addWidget(self._spin)
            ctrl_row.addWidget(QLabel(f"/ {n_pages}"))
            self._spin.valueChanged.connect(lambda v: self._load_page(v - 1))

        layout.addLayout(ctrl_row)

        # --- Area di scorrimento ---
        self._scroll = _ZoomScrollArea(self._on_wheel)
        self._scroll.setWidgetResizable(False)
        self._scroll.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self._scroll.setAlignment(Qt.AlignCenter)

        self._img_label = QLabel()
        self._img_label.setObjectName("img_label")
        self._img_label.setAlignment(Qt.AlignCenter)
        self._img_label.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self._scroll.setWidget(self._img_label)
        layout.addWidget(self._scroll, stretch=1)

        if pil_img:
            self._load_page(0)
        else:
            self._img_label.setText(_gm(gd, "Anteprima non disponibile", lg))

    # ------------------------------------------------------------------
    def _load_page(self, idx: int):
        """Carica il frame idx e salva il pixmap base."""
        if not self._pil_img:
            return
        try:
            if self._n_pages > 1:
                self._pil_img.seek(idx)
            self._base_pix = _pil_to_qpixmap(self._pil_img)
            if self._fit_mode:
                self._fit_to_view()
            else:
                self._apply_zoom()
        except Exception as exc:
            err = _gm(self._glossario_data, "Errore nel caricamento", self._lingua)
            self._img_label.setText(f"{err}: {exc}")

    def _apply_zoom(self):
        if not self._base_pix:
            return
        w = int(self._base_pix.width()  * self._zoom)
        h = int(self._base_pix.height() * self._zoom)
        scaled = self._base_pix.scaled(w, h, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self._img_label.setPixmap(scaled)
        self._img_label.resize(scaled.size())
        self._lbl_zoom.setText(f"{int(self._zoom * 100)}%")

    def _fit_to_view(self):
        if not self._base_pix:
            return
        self._fit_mode = True
        vp = self._scroll.viewport()
        avail_w = max(vp.width()  - 4, 100)
        avail_h = max(vp.height() - 4, 100)
        scaled = self._base_pix.scaled(
            avail_w, avail_h, Qt.KeepAspectRatio, Qt.SmoothTransformation
        )
        self._zoom = scaled.width() / max(self._base_pix.width(), 1)
        self._img_label.setPixmap(scaled)
        self._img_label.resize(scaled.size())
        self._lbl_zoom.setText(f"{int(self._zoom * 100)}%")

    def _zoom_1to1(self):
        self._fit_mode = False
        self._zoom = 1.0
        self._apply_zoom()

    def _zoom_in(self):
        self._fit_mode = False
        self._zoom = min(self._zoom + self._ZOOM_STEP, self._ZOOM_MAX)
        self._apply_zoom()

    def _zoom_out(self):
        self._fit_mode = False
        self._zoom = max(self._zoom - self._ZOOM_STEP, self._ZOOM_MIN)
        self._apply_zoom()

    def _on_wheel(self, delta: int):
        """Chiamato da _ZoomScrollArea quando Ctrl+Rotella."""
        if delta > 0:
            self._zoom_in()
        else:
            self._zoom_out()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        # Ricalcola adatta-alla-finestra se in fit_mode
        if self._fit_mode and self._base_pix:
            self._fit_to_view()


# ---------------------------------------------------------------------------
# Widget pannello metadati JSON
# ---------------------------------------------------------------------------
class _MetaPanel(QWidget):
    """Pannello con QTreeWidget che mostra le coppie chiave/valore del JSON."""

    def __init__(self, meta: dict, parent=None, glossario_data=None, lingua: str = "IT"):
        super().__init__(parent)
        from PySide6.QtWidgets import QHeaderView
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        tree = QTreeWidget()
        tree.setAlternatingRowColors(True)
        tree.setColumnCount(2)
        gd, lg = glossario_data, lingua
        tree.setHeaderLabels([_gm(gd, "Campo", lg), _gm(gd, "Valore metadato", lg)])
        tree.setSortingEnabled(False)

        for key, value in meta.items():
            # Salta i campi interni (non destinati alla visualizzazione)
            if str(key).startswith("_"):
                continue
            # Localizza il nome del campo tramite glossario;
            # _gm restituisce il messaggio localizzato o, come fallback, la chiave stessa.
            display_key = _gm(gd, str(key), lg) if gd else str(key)
            item = QTreeWidgetItem([display_key, str(value)])
            tree.addTopLevelItem(item)

        # Ridimensiona entrambe le colonne in base al contenuto
        tree.resizeColumnToContents(0)
        tree.resizeColumnToContents(1)
        # Colonna 0 fissa al contenuto, colonna 1 si allarga con la finestra
        tree.header().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        tree.header().setSectionResizeMode(1, QHeaderView.Stretch)
        tree.header().setMinimumSectionSize(80)
        tree.header().setDefaultSectionSize(44)
        tree.header().setDefaultAlignment(Qt.AlignVCenter | Qt.AlignLeft)
        tree.header().setStyleSheet(
            "QHeaderView::section {"
            "  background-color: #2a2a2a;"
            "  color: #a67c52;"
            "  border: 1px solid #a67c52;"
            "  padding: 8px 10px;"
            "  font-weight: bold;"
            "  font-size: 13px;"
            "  height: 44px;"
            "}"
        )
        tree.setMinimumWidth(320)
        layout.addWidget(tree)


# ---------------------------------------------------------------------------
# Dialog base condiviso
# ---------------------------------------------------------------------------
def _make_base_dialog(parent, title: str, width: int = 1100, height: int = 700) -> QDialog:
    dlg = QDialog(parent)
    dlg.setWindowTitle(title)
    # Flag standard: minimizza, massimizza, chiudi
    dlg.setWindowFlags(
        Qt.Window
        | Qt.WindowMinimizeButtonHint
        | Qt.WindowMaximizeButtonHint
        | Qt.WindowCloseButtonHint
    )
    dlg.resize(width, height)
    dlg.setStyleSheet(_DARK_STYLE)
    try:
        from asset_cache import get_pixmap_cached  # type: ignore
        from main_gui_qt import asset_path  # type: ignore
        dlg.setWindowIcon(QIcon(get_pixmap_cached(asset_path("assets/common/grafici/ATK-Pro.ico"))))
    except Exception:
        pass
    return dlg


def _add_close_button(layout: QVBoxLayout, dlg: QDialog, label: str = "Chiudi"):
    row = QHBoxLayout()
    row.addStretch()
    btn = QPushButton(label)
    btn.setMinimumWidth(80)
    btn.clicked.connect(dlg.accept)
    row.addWidget(btn)
    layout.addLayout(row)


# ---------------------------------------------------------------------------
# API pubblica
# ---------------------------------------------------------------------------

def apri_visualizzatore_immagini(parent, glossario_data=None, lingua: str = "IT",
                                  output_folder: str | None = None):
    """
    Apre un file immagine (JPG/PNG/TIFF) con anteprima a sinistra e
    metadati JSON sidecar a destra (se disponibile).
    """
    gd, lg = glossario_data, lingua
    start_dir = output_folder or ""
    tutti = _gm(gd, "Tutti i file", lg)
    path, _ = QFileDialog.getOpenFileName(
        parent,
        _gm(gd, "Apri immagine", lg),
        start_dir,
        f"Immagini (*.jpg *.jpeg *.png *.tif *.tiff);;{tutti} (*)"
    )
    if not path:
        return

    pil_img = _load_pil(path)
    if pil_img is None:
        err_title = _gm(gd, "Errore", lg)
        err_msg   = _gm(gd, "Impossibile aprire l'immagine", lg)
        err_hint  = _gm(gd, "Assicurarsi che Pillow sia installato", lg)
        QMessageBox.critical(parent, err_title, f"{err_msg}.\n{err_hint}.")
        return

    n_pages = getattr(pil_img, "n_frames", 1)
    title = os.path.basename(path)

    dlg = _make_base_dialog(parent, title, width=1200, height=750)
    main_layout = QVBoxLayout(dlg)
    main_layout.setContentsMargins(10, 10, 10, 10)
    main_layout.setSpacing(8)

    splitter = QSplitter(Qt.Horizontal)

    # Pannello sinistro: immagine
    img_panel = _ImagePanel(pil_img=pil_img, n_pages=n_pages,
                             glossario_data=gd, lingua=lg)
    splitter.addWidget(img_panel)

    # Pannello destro: metadati (se sidecar presente)
    json_path = _find_json_for_image(path)
    if json_path:
        try:
            with open(json_path, encoding="utf-8") as fh:
                meta = json.load(fh)
            meta_widget = _MetaPanel(meta, glossario_data=gd, lingua=lg)
            splitter.addWidget(meta_widget)
            splitter.setSizes([750, 350])
        except Exception as exc:
            meta_widget = QLabel(f"{_gm(gd, 'Errore lettura metadati', lg)}:\n{exc}")
            meta_widget.setAlignment(Qt.AlignCenter)
            splitter.addWidget(meta_widget)
            splitter.setSizes([750, 350])
    else:
        meta_widget = QLabel(_gm(gd, "Nessun sidecar JSON trovato", lg))
        meta_widget.setAlignment(Qt.AlignCenter)
        meta_widget.setStyleSheet("color: #888; font-size: 13px;")
        splitter.addWidget(meta_widget)
        splitter.setSizes([800, 300])

    _saved_sizes = [splitter.sizes()]

    def _toggle_meta():
        if meta_widget.isVisible():
            _saved_sizes[0] = splitter.sizes()
            meta_widget.setVisible(False)
            btn_toggle.setText("\u25b6  " + _gm(gd, "Mostra metadati", lg))
        else:
            meta_widget.setVisible(True)
            splitter.setSizes(_saved_sizes[0])
            btn_toggle.setText("\u25c4  " + _gm(gd, "Nascondi metadati", lg))

    toolbar = QHBoxLayout()
    toolbar.setContentsMargins(0, 0, 0, 0)
    toolbar.addStretch()
    btn_toggle = QPushButton("\u25c4  " + _gm(gd, "Nascondi metadati", lg))
    btn_toggle.setMinimumWidth(160)
    btn_toggle.clicked.connect(_toggle_meta)
    toolbar.addWidget(btn_toggle)

    main_layout.addLayout(toolbar)
    main_layout.addWidget(splitter, stretch=1)
    _add_close_button(main_layout, dlg, _gm(gd, "Chiudi", lg))
    dlg.exec()


def apri_visualizzatore_metadati(parent, glossario_data=None, lingua: str = "IT",
                                  output_folder: str | None = None):
    """
    Apre un file JSON sidecar con i metadati a sinistra e
    l'immagine abbinata a destra (se disponibile).
    """
    gd, lg = glossario_data, lingua
    start_dir = output_folder or ""
    tutti = _gm(gd, "Tutti i file", lg)
    path, _ = QFileDialog.getOpenFileName(
        parent,
        _gm(gd, "Apri metadati JSON", lg),
        start_dir,
        f"File JSON (*.json);;{tutti} (*)"
    )
    if not path:
        return

    try:
        with open(path, encoding="utf-8") as fh:
            meta = json.load(fh)
    except Exception as exc:
        err_title = _gm(gd, "Errore", lg)
        err_msg   = _gm(gd, "Impossibile leggere il file JSON", lg)
        QMessageBox.critical(parent, err_title, f"{err_msg}:\n{exc}")
        return

    title = os.path.basename(path)
    dlg = _make_base_dialog(parent, title, width=1100, height=700)
    main_layout = QVBoxLayout(dlg)
    main_layout.setContentsMargins(10, 10, 10, 10)
    main_layout.setSpacing(8)

    splitter = QSplitter(Qt.Horizontal)

    # Pannello sinistro: metadati
    meta_panel = _MetaPanel(meta, glossario_data=gd, lingua=lg)
    splitter.addWidget(meta_panel)

    # Pannello destro: anteprima immagine abbinata
    img_path = _find_image_for_json(path)
    if img_path:
        pil_img = _load_pil(img_path)
        n_pages = getattr(pil_img, "n_frames", 1) if pil_img else 1
        img_panel = _ImagePanel(pil_img=pil_img, n_pages=n_pages,
                                 glossario_data=gd, lingua=lg)
        splitter.addWidget(img_panel)
        splitter.setSizes([420, 580])
    else:
        lbl = QLabel(_gm(gd, "Nessuna immagine abbinata trovata", lg))
        lbl.setAlignment(Qt.AlignCenter)
        lbl.setStyleSheet("color: #888; font-size: 13px;")
        splitter.addWidget(lbl)
        splitter.setSizes([500, 500])

    _saved_sizes = [splitter.sizes()]

    def _toggle_meta():
        if meta_panel.isVisible():
            _saved_sizes[0] = splitter.sizes()
            meta_panel.setVisible(False)
            btn_toggle.setText("\u25b6  " + _gm(gd, "Mostra metadati", lg))
        else:
            meta_panel.setVisible(True)
            splitter.setSizes(_saved_sizes[0])
            btn_toggle.setText("\u25c4  " + _gm(gd, "Nascondi metadati", lg))

    toolbar = QHBoxLayout()
    toolbar.setContentsMargins(0, 0, 0, 0)
    toolbar.addStretch()
    btn_toggle = QPushButton("\u25c4  " + _gm(gd, "Nascondi metadati", lg))
    btn_toggle.setMinimumWidth(160)
    btn_toggle.clicked.connect(_toggle_meta)
    toolbar.addWidget(btn_toggle)

    main_layout.addLayout(toolbar)
    main_layout.addWidget(splitter, stretch=1)
    _add_close_button(main_layout, dlg, _gm(gd, "Chiudi", lg))
    dlg.exec()
