import json
from pathlib import Path

from PySide6.QtWidgets import QDialog, QPushButton, QTextEdit

from src.main_gui_qt import (
    _build_atk_text_document_dialog,
    _localized_disclaimer_html_path,
    show_operation_completed_dialog,
)


def test_text_document_dialog_uses_atk_pro_style(qtbot):
    dialog = _build_atk_text_document_dialog(
        None,
        "Disclaimer",
        "Testo legale invariato.",
        "Chiudi",
    )
    qtbot.addWidget(dialog)

    style = dialog.styleSheet()
    assert "background-color: #181818" in style
    assert "border: 2px solid #a67c52" in style

    text = dialog.findChild(QTextEdit)
    assert text is not None
    assert text.isReadOnly()
    assert text.toPlainText() == "Testo legale invariato."
    assert "rgba(255, 255, 255, 220)" in text.styleSheet()

    buttons = dialog.findChildren(QPushButton)
    assert [button.text() for button in buttons] == ["Chiudi"]


def test_disclaimer_document_prefers_localized_html_and_falls_back_to_italian(tmp_path, monkeypatch):
    import src.main_gui_qt as gui

    italian = tmp_path / "it" / "testuali" / "disclaimer_legale_ATK-Pro.html"
    english = tmp_path / "en" / "testuali" / "disclaimer_legale_ATK-Pro.html"
    italian.parent.mkdir(parents=True)
    english.parent.mkdir(parents=True)
    italian.write_text("italiano", encoding="utf-8")
    english.write_text("english", encoding="utf-8")
    monkeypatch.setattr(gui, "ASSET_LANG", str(tmp_path))

    assert _localized_disclaimer_html_path("en") == str(english)
    assert _localized_disclaimer_html_path("xx") == str(italian)


def test_completion_dialog_warns_when_pdf_contains_placeholders(qtbot, monkeypatch):
    glossary_path = (
        Path(__file__).parents[1]
        / "docs_generali"
        / "glossario_multilingua_ATK-Pro.json"
    )
    glossary = json.loads(glossary_path.read_text(encoding="utf-8"))
    captured = {}

    def capture_dialog(dialog):
        captured["title"] = dialog.windowTitle()
        reports = dialog.findChildren(QTextEdit)
        captured["report"] = reports[0].toPlainText() if reports else ""
        return 0

    monkeypatch.setattr(QDialog, "exec", capture_dialog)

    show_operation_completed_dialog(None, glossary, "IT", [{
        "file": "registro.pdf",
        "status": "INCOMPLETE",
        "formati": ["PDF"],
        "placeholder_count": 1,
        "placeholder_images": [{"canvas": "page_7", "label": "Pagina 7"}],
    }])

    assert captured["title"] == "PDF incompleto"
    assert "Output incompleto: 1 pagine sostituite da placeholder" in captured["report"]
    assert "Pagina non recuperata: Pagina 7" in captured["report"]
