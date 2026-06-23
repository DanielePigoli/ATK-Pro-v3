# test_ui_info.py
import importlib
import types

def test_ui_info_constants():
    ui_info = importlib.import_module("ui_info")

    # Verifica che il modulo sia stato caricato
    assert isinstance(ui_info, types.ModuleType)

    # Verifica che le costanti esistano e siano stringhe non vuote
    for attr in ("APP_NAME", "WELCOME_MSG", "HELP_TEXT"):
        value = getattr(ui_info, attr, None)
        assert isinstance(value, str), f"{attr} non è una stringa"
        assert value.strip(), f"{attr} è vuoto"

def test_ui_info_localization():
    ui_info = importlib.import_module("ui_info")
    # gettext deve restituire le stesse stringhe definite
    assert ui_info.APP_NAME == "Antenati ToolKit Pro"
    assert "ATK‑Pro v3.0.0 RC2" in ui_info.WELCOME_MSG
    assert "CLI" in ui_info.HELP_TEXT
