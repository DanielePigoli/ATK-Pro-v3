import json
import logging

import pytest

from src import config_utils
from src import main_gui_qt
from src.resource_profile import RESOURCE_PROFILE_BALANCED, RESOURCE_PROFILE_FAST


def _point_gui_to(monkeypatch, config_path):
    monkeypatch.setattr(main_gui_qt, "_config_file_path", lambda: str(config_path))
    monkeypatch.setattr(main_gui_qt, "_CONFIG_PREFS_CACHE_PATH", None)
    monkeypatch.setattr(main_gui_qt, "_CONFIG_PREFS_CACHE_SIGNATURE", None)
    monkeypatch.setattr(main_gui_qt, "_CONFIG_PREFS_CACHE_VALUE", None)


def test_config_path_uses_executable_directory_in_portable_mode(tmp_path, monkeypatch):
    monkeypatch.setattr(config_utils, "IS_PORTABLE", True)
    monkeypatch.setattr(config_utils, "_EXE_DIR", str(tmp_path))

    assert config_utils._config_file_path() == str(tmp_path / "config.json")


def test_config_path_uses_user_config_directory_when_installed(tmp_path, monkeypatch):
    monkeypatch.setattr(config_utils, "IS_PORTABLE", False)
    monkeypatch.setattr(config_utils.os.path, "expanduser", lambda value: str(tmp_path))

    assert config_utils._config_file_path() == str(
        tmp_path / ".config" / "atk-pro" / "config.json"
    )


def test_update_creates_missing_config_and_parent_directory(tmp_path):
    config_path = tmp_path / "nested" / "config.json"

    backup = config_utils._update_config_file(
        str(config_path),
        {"language": "it", "formats": ["PNG"]},
    )

    assert backup is None
    assert json.loads(config_path.read_text(encoding="utf-8")) == {
        "language": "it",
        "formats": ["PNG"],
    }


def test_update_preserves_existing_unknown_keys_and_unicode(tmp_path):
    config_path = tmp_path / "config.json"
    config_path.write_text(
        json.dumps({"future_option": "già presente", "language": "en"}),
        encoding="utf-8",
    )

    config_utils._update_config_file(str(config_path), {"language": "it"})

    saved = json.loads(config_path.read_text(encoding="utf-8"))
    assert saved == {"future_option": "già presente", "language": "it"}
    assert "già presente" in config_path.read_text(encoding="utf-8")


def test_malformed_json_is_backed_up_and_rebuilt(tmp_path):
    config_path = tmp_path / "config.json"
    corrupt_text = '{"language": "it", broken'
    config_path.write_text(corrupt_text, encoding="utf-8")

    backup = config_utils._update_config_file(
        str(config_path),
        {"resource_profile": RESOURCE_PROFILE_FAST},
    )

    assert backup == str(config_path) + ".corrupt"
    assert (tmp_path / "config.json.corrupt").read_text(encoding="utf-8") == corrupt_text
    assert json.loads(config_path.read_text(encoding="utf-8")) == {
        "resource_profile": RESOURCE_PROFILE_FAST,
    }


@pytest.mark.parametrize("invalid_root", [[], ["it"], None, "it"])
def test_non_object_json_is_backed_up_and_rebuilt(tmp_path, invalid_root):
    config_path = tmp_path / "config.json"
    config_path.write_text(json.dumps(invalid_root), encoding="utf-8")

    backup = config_utils._update_config_file(str(config_path), {"language": "it"})

    assert backup == str(config_path) + ".corrupt"
    assert json.loads(config_path.read_text(encoding="utf-8")) == {"language": "it"}
    assert json.loads((tmp_path / "config.json.corrupt").read_text(encoding="utf-8")) == invalid_root


def test_repeated_recovery_never_overwrites_previous_backup(tmp_path):
    config_path = tmp_path / "config.json"
    config_path.write_text("{first", encoding="utf-8")
    first_backup = config_utils._update_config_file(str(config_path), {"language": "it"})

    config_path.write_text("{second", encoding="utf-8")
    second_backup = config_utils._update_config_file(str(config_path), {"language": "en"})

    assert first_backup == str(config_path) + ".corrupt"
    assert second_backup == str(config_path) + ".corrupt.1"
    assert (tmp_path / "config.json.corrupt").read_text(encoding="utf-8") == "{first"
    assert (tmp_path / "config.json.corrupt.1").read_text(encoding="utf-8") == "{second"


def test_replace_failure_preserves_original_and_removes_temp_file(tmp_path, monkeypatch):
    config_path = tmp_path / "config.json"
    original = '{"language": "en"}'
    config_path.write_text(original, encoding="utf-8")
    monkeypatch.setattr(
        config_utils.os,
        "replace",
        lambda *_: (_ for _ in ()).throw(OSError("replace denied")),
    )

    with pytest.raises(OSError, match="replace denied"):
        config_utils._update_config_file(str(config_path), {"language": "it"})

    assert config_path.read_text(encoding="utf-8") == original
    assert list(tmp_path.glob(".config.json.*.tmp")) == []


def test_serialization_failure_preserves_original_and_removes_temp_file(tmp_path):
    config_path = tmp_path / "config.json"
    original = '{"language": "en"}'
    config_path.write_text(original, encoding="utf-8")

    with pytest.raises(TypeError):
        config_utils._update_config_file(str(config_path), {"invalid": object()})

    assert config_path.read_text(encoding="utf-8") == original
    assert list(tmp_path.glob(".config.json.*.tmp")) == []


def test_public_preference_writer_reports_failure_without_logging_secret(
    tmp_path,
    monkeypatch,
    caplog,
):
    config_path = tmp_path / "config.json"
    monkeypatch.setattr(config_utils, "_config_file_path", lambda: str(config_path))
    monkeypatch.setattr(
        config_utils,
        "_update_config_file",
        lambda *_: (_ for _ in ()).throw(OSError("read only")),
    )

    with caplog.at_level(logging.WARNING):
        saved = config_utils._write_config_prefs("ocr_api_key", "TOP-SECRET")

    assert saved is False
    assert "ocr_api_key" in caplog.text
    assert "TOP-SECRET" not in caplog.text


def test_gui_read_uses_defaults_when_config_is_missing(tmp_path, monkeypatch):
    config_path = tmp_path / "config.json"
    _point_gui_to(monkeypatch, config_path)

    prefs = main_gui_qt._read_config_prefs()

    assert prefs["portale_attivo"] == "antenati"
    assert prefs["resource_profile"] == RESOURCE_PROFILE_BALANCED


def test_gui_write_recovers_corrupt_config_and_refreshes_cache(tmp_path, monkeypatch):
    config_path = tmp_path / "config.json"
    config_path.write_text("{broken", encoding="utf-8")
    _point_gui_to(monkeypatch, config_path)

    defaults = main_gui_qt._read_config_prefs()
    saved = main_gui_qt._write_config_prefs("resource_profile", RESOURCE_PROFILE_FAST)
    refreshed = main_gui_qt._read_config_prefs()

    assert defaults["resource_profile"] == RESOURCE_PROFILE_BALANCED
    assert saved is True
    assert refreshed["resource_profile"] == RESOURCE_PROFILE_FAST
    assert (tmp_path / "config.json.corrupt").read_text(encoding="utf-8") == "{broken"


def test_gui_failed_write_does_not_publish_unsaved_cache_value(tmp_path, monkeypatch):
    config_path = tmp_path / "config.json"
    config_path.write_text(
        json.dumps({"resource_profile": RESOURCE_PROFILE_BALANCED}),
        encoding="utf-8",
    )
    _point_gui_to(monkeypatch, config_path)
    assert main_gui_qt._read_config_prefs()["resource_profile"] == RESOURCE_PROFILE_BALANCED
    monkeypatch.setattr(
        main_gui_qt,
        "_update_config_file",
        lambda *_: (_ for _ in ()).throw(OSError("read only")),
    )

    saved = main_gui_qt._write_config_prefs("resource_profile", RESOURCE_PROFILE_FAST)

    assert saved is False
    assert main_gui_qt._read_config_prefs()["resource_profile"] == RESOURCE_PROFILE_BALANCED


def test_language_write_recovers_corrupt_config(tmp_path, monkeypatch):
    config_path = tmp_path / "config.json"
    config_path.write_text("{broken-language", encoding="utf-8")
    _point_gui_to(monkeypatch, config_path)

    main_gui_qt._write_config_language("it")

    assert json.loads(config_path.read_text(encoding="utf-8")) == {"language": "it"}
    assert (tmp_path / "config.json.corrupt").read_text(encoding="utf-8") == "{broken-language"


def test_disclaimer_write_recovers_corrupt_config(tmp_path, monkeypatch):
    config_path = tmp_path / "config.json"
    config_path.write_text("{broken-disclaimer", encoding="utf-8")
    _point_gui_to(monkeypatch, config_path)

    main_gui_qt._write_config_disclaimer_accepted()

    saved = json.loads(config_path.read_text(encoding="utf-8"))
    assert saved["disclaimer_accepted"] is True
    assert saved["disclaimer_revision"] == main_gui_qt.DISCLAIMER_REVISION
    assert saved["disclaimer_accepted_version"] == main_gui_qt.VERSION
    assert (tmp_path / "config.json.corrupt").read_text(encoding="utf-8") == "{broken-disclaimer"
