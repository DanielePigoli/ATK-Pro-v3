import json

from src.main_gui_qt import (
    DISCLAIMER_REVISION,
    _read_config_prefs,
    _write_config_disclaimer_accepted,
    _write_config_prefs,
    _write_config_prefs_batch,
)
from src.atk_version import VERSION
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


def test_read_config_prefs_reloads_when_file_changes(tmp_path, monkeypatch):
    config_path = tmp_path / "atk_config.json"
    config_path.write_text(json.dumps({"resource_profile": RESOURCE_PROFILE_FAST}), encoding="utf-8")

    monkeypatch.setattr("src.main_gui_qt._config_file_path", lambda: str(config_path))

    first = _read_config_prefs()
    assert first["resource_profile"] == RESOURCE_PROFILE_FAST

    config_path.write_text(json.dumps({"resource_profile": RESOURCE_PROFILE_BALANCED}), encoding="utf-8")

    second = _read_config_prefs()
    assert second["resource_profile"] == RESOURCE_PROFILE_BALANCED


def test_write_config_prefs_updates_cached_value(tmp_path, monkeypatch):
    config_path = tmp_path / "atk_config.json"
    config_path.write_text(json.dumps({}), encoding="utf-8")

    monkeypatch.setattr("src.main_gui_qt._config_file_path", lambda: str(config_path))

    _write_config_prefs("resource_profile", RESOURCE_PROFILE_FAST)
    prefs = _read_config_prefs()

    assert prefs["resource_profile"] == RESOURCE_PROFILE_FAST


def test_write_config_prefs_batch_updates_multiple_values(tmp_path, monkeypatch):
    config_path = tmp_path / "atk_config.json"
    config_path.write_text(json.dumps({}), encoding="utf-8")

    monkeypatch.setattr("src.main_gui_qt._config_file_path", lambda: str(config_path))

    _write_config_prefs_batch(
        {
            "resource_profile": RESOURCE_PROFILE_FAST,
            "portale_attivo": "dl_ficlit",
        }
    )

    prefs = _read_config_prefs()

    assert prefs["resource_profile"] == RESOURCE_PROFILE_FAST
    assert prefs["portale_attivo"] == "dl_ficlit"


def test_write_config_disclaimer_accepted_persists_all_keys(tmp_path, monkeypatch):
    config_path = tmp_path / "atk_config.json"
    config_path.write_text(json.dumps({}), encoding="utf-8")

    monkeypatch.setattr("src.main_gui_qt._config_file_path", lambda: str(config_path))

    _write_config_disclaimer_accepted()

    saved = json.loads(config_path.read_text(encoding="utf-8"))
    assert saved["disclaimer_accepted"] is True
    assert saved["disclaimer_revision"] == DISCLAIMER_REVISION
    assert saved["disclaimer_accepted_version"] == VERSION
