from pathlib import Path


def test_main_gui_avoids_top_level_elaborazione_import():
    source = Path("src/main_gui_qt.py").read_text(encoding="utf-8")

    assert "\nimport elaborazione as elaborazione_mod\n" not in source
    assert "def _get_elaborazione_module():" in source
    assert "_get_elaborazione_module().esegui_elaborazione(" in source
