from PySide6.QtWidgets import QPushButton, QTextEdit

from src.main_gui_qt import _build_atk_text_document_dialog


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
