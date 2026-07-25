from src import main_gui_qt as gui
from src.resource_profile import RESOURCE_PROFILE_BALANCED


def test_build_initial_state_includes_runtime_defaults():
    state = gui._build_initial_state()

    assert state == {
        "records": [],
        "formats": [],
        "output_folder": None,
        "registri_output": [],
        "current_input_file": None,
        "resource_profile": RESOURCE_PROFILE_BALANCED,
    }


def test_global_state_starts_from_initial_defaults():
    assert gui.state["resource_profile"] == RESOURCE_PROFILE_BALANCED
    assert gui.state["current_input_file"] is None


def test_prompt_for_formats_after_input_load_updates_state_once(monkeypatch):
    original_formats = gui.state.get("formats")
    persisted_formats = []

    monkeypatch.setattr(gui, "ask_image_formats", lambda glossario, lingua: ["PNG", "PDF"])
    monkeypatch.setattr(gui, "_write_config_prefs", lambda key, value: persisted_formats.append((key, value)))

    gui.state["formats"] = []
    try:
        selected = gui._prompt_for_formats_after_input_load(None, "it")
        state_formats = list(gui.state["formats"])
    finally:
        gui.state["formats"] = original_formats

    assert selected == ["PNG", "PDF"]
    assert state_formats == ["PNG", "PDF"]
    assert persisted_formats == []
