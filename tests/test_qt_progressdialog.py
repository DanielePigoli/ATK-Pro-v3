import os
import time
from PySide6.QtCore import Qt

import pytest

from src.user_prompts import ProgressDialog


def test_progressdialog_cancel_and_center(qtbot):
    # Ensure headless mode for CI/Windows
    os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')

    pd = ProgressDialog(glossario_data=None, lingua='IT', total=3, parent=None)
    assert pd._use_qt is True

    # Register widget with qtbot and show
    qtbot.addWidget(pd.dialog)
    pd.show()
    # wait until visible
    qtbot.waitUntil(lambda: pd.dialog.isVisible(), timeout=2000)

    # Update and check label text contains progress and name
    pd.update(1, name='Registro 1')
    assert 'Record 1/3' in pd.label.text()
    assert 'Registro 1' in pd.label.text()

    # Click cancel and verify cancelled flag is set
    qtbot.mouseClick(pd.cancel_btn, Qt.LeftButton)
    qtbot.waitUntil(lambda: getattr(pd, 'cancelled', False) is True, timeout=1000)
    assert pd.cancelled is True

    pd.close()
