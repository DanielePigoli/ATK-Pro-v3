from pathlib import PureWindowsPath

import pytest

from src.path_policy import (
    ONEDRIVE,
    WINDOWS_DESKTOP,
    detect_profile,
    evaluate_paths,
    preflight_record,
)


def test_detects_onedrive_only_when_root_contains_onedrive():
    assert detect_profile(r"C:\Users\Ada\OneDrive - Ente\ATK") is ONEDRIVE
    assert detect_profile(r"C:\Archivi\ATK") is WINDOWS_DESKTOP
    assert detect_profile(r"C:\Archivi\OneDriveBackup\ATK") is WINDOWS_DESKTOP


def test_windows_drive_anchor_is_not_treated_as_invalid_segment():
    report = evaluate_paths([r"C:\Archivi\ATK\record.pdf"], WINDOWS_DESKTOP)
    assert not [issue for issue in report.errors if issue.code == "invalid_character"]


def test_legacy_windows_length_is_a_warning_not_a_global_block():
    path = str(PureWindowsPath(r"C:\Archivi", *("a" * 80 for _ in range(4)), "record.pdf"))
    report = evaluate_paths([path], WINDOWS_DESKTOP)
    assert not report.errors
    assert any(issue.code == "absolute_local" for issue in report.warnings)


def test_onedrive_sync_limit_is_blocking_only_in_onedrive_profile():
    path = str(PureWindowsPath(r"C:\Users\Ada\OneDrive - Ente", *("a" * 100 for _ in range(5)), "record.pdf"))
    report = evaluate_paths([path], ONEDRIVE)
    assert any(issue.code == "onedrive_sync" for issue in report.errors)


def test_raw_user_name_is_rejected_instead_of_silently_sanitized():
    report = preflight_record(
        r"C:\Archivi\ATK",
        "registro: 1901",
        "R",
        ["PDF", "JPG"],
        profile=WINDOWS_DESKTOP,
    )
    assert any(issue.code == "invalid_character" for issue in report.errors)
    with pytest.raises(ValueError):
        report.raise_for_errors()
