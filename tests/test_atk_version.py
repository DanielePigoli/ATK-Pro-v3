from src.atk_version import DISPLAY_VERSION, VERSION, is_newer_version


def test_rc_version_identifiers_are_distinct():
    assert VERSION == "3.0.0-rc1"
    assert DISPLAY_VERSION == "3.0.0 RC1"


def test_final_release_is_newer_than_rc():
    assert is_newer_version("3.0.0") is True


def test_older_or_invalid_release_is_not_newer():
    assert is_newer_version("3.0.0-rc1") is False
    assert is_newer_version("2.9.9") is False
    assert is_newer_version("") is False
