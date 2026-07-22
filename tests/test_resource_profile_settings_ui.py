import json

from src.main_gui_qt import _read_config_prefs
from src.resource_profile import RESOURCE_PROFILE_BALANCED, RESOURCE_PROFILE_FAST


def test_read_config_prefs_restores_saved_resource_profile(tmp_path, monkeypatch):
    config_path = tmp_path / "atk_config.json"
    config_path.write_text(json.dumps({"resource_profile": RESOURCE_PROFILE_FAST}), encoding="utf-8")

    monkeypatch.setattr("src.main_gui_qt._config_file_path", lambda: str(config_path))

    prefs = _read_config_prefs()

    assert prefs["resource_profile"] == RESOURCE_PROFILE_FAST


def test_read_config_prefs_normalizes_invalid_resource_profile(tmp_path, monkeypatch):
    config_path = tmp_path / "atk_config.json"
    config_path.write_text(json.dumps({"resource_profile": "turbo"}), encoding="utf-8")

    monkeypatch.setattr("src.main_gui_qt._config_file_path", lambda: str(config_path))

    prefs = _read_config_prefs()

    assert prefs["resource_profile"] == RESOURCE_PROFILE_BALANCED
