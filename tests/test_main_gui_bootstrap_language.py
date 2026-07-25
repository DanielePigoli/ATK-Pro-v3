from src import main_gui_qt as gui


def test_resolve_initial_language_prefers_saved_config_in_dev(monkeypatch):
    monkeypatch.setattr(gui.sys, "platform", "win32")
    monkeypatch.setattr(gui.sys, "frozen", False, raising=False)
    monkeypatch.setattr(gui, "_read_config_language", lambda: "it")
    monkeypatch.setattr(gui, "_choose_and_persist_language", lambda default="en": "en")

    lingua, primo_avvio = gui._resolve_initial_language()

    assert lingua == "it"
    assert primo_avvio is False


def test_resolve_initial_language_uses_portable_selector_on_first_run(monkeypatch):
    monkeypatch.setattr(gui.sys, "platform", "win32")
    monkeypatch.setattr(gui.sys, "frozen", True, raising=False)
    monkeypatch.setattr(gui, "IS_PORTABLE", True)
    monkeypatch.setattr(gui, "_read_config_language", lambda: None)
    monkeypatch.setattr(gui, "_choose_and_persist_language", lambda default="en": "de")

    lingua, primo_avvio = gui._resolve_initial_language()

    assert lingua == "de"
    assert primo_avvio is True
