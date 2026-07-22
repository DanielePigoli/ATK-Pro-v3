from pathlib import Path


def test_main_gui_avoids_top_level_input_imports():
    source = Path("src/main_gui_qt.py").read_text(encoding="utf-8")

    assert "\nfrom input_loader import load_input_file\n" not in source
    assert "\nfrom input_parser import parse_input_text\n" not in source
    assert "def _get_input_helpers():" in source
    assert "load_input_file, parse_input_text = _get_input_helpers()" in source
