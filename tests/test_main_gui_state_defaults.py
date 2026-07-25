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
