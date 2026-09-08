from src.atk_version import DISPLAY_VERSION, VERSION, is_newer_version


def test_stable_version_identifiers():
    assert VERSION == "3.0.0"
    assert DISPLAY_VERSION == "3.0.0"


def test_final_release_is_newer_than_rc():
    assert is_newer_version("3.0.0", current="3.0.0-rc4") is True


def test_newer_release_is_detected_from_stable():
    assert is_newer_version("3.0.1") is True


def test_older_current_or_invalid_release_is_not_newer():
    assert is_newer_version("3.0.0-rc1") is False
    assert is_newer_version("3.0.0-rc2") is False
    assert is_newer_version("3.0.0-rc3") is False
    assert is_newer_version("3.0.0-rc4") is False
    assert is_newer_version("3.0.0") is False
    assert is_newer_version("2.9.9") is False
    assert is_newer_version("") is False
