# -*- coding: utf-8 -*-

from pathlib import Path


def test_main_window_processing_does_not_call_legacy_esegui_elaborazione_fallback():
    source = Path("src/main_gui_qt.py").read_text(encoding="utf-8")
    assert "elaborazione.esegui_elaborazione(state, glossario, lingua, records, formats)" not in source
