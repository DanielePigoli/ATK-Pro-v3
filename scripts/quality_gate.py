#!/usr/bin/env python3
"""Canonical PR smoke and release quality gates for ATK-Pro."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PYTHON = sys.executable

STATIC_CHECKS = [
    [PYTHON, "verify_localization.py"],
    [PYTHON, "validate_glossary.py"],
    [PYTHON, "verify_glossary.py"],
    [PYTHON, "verify_disclaimer_consent.py"],
    [PYTHON, "verify_document_assets.py"],
    [PYTHON, "verify_italian_guide_content.py"],
    [PYTHON, "verify_portal_matrix_workbook.py"],
    [PYTHON, "verify_portal_policy.py", "--strict"],
    [PYTHON, "scripts/verify_release_hygiene.py"],
]

COMPILE_CHECK = [
    PYTHON,
    "-m",
    "py_compile",
    "src/main_gui_qt.py",
    "src/elaborazione.py",
    "src/manifest_utils.py",
    "src/tile_downloader.py",
    "src/qt_worker.py",
    "src/portal_registry.py",
    "verify_localization.py",
    "verify_disclaimer_consent.py",
    "verify_document_assets.py",
    "verify_italian_guide_content.py",
    "verify_portal_matrix_workbook.py",
    "verify_portal_live_smoke.py",
    "verify_manifest_url.py",
    "verify_portal_policy.py",
]

SMOKE_TESTS = [
    PYTHON,
    "-m",
    "pytest",
    "tests/test_manifest_utils.py",
    "tests/test_manifest_parser.py",
    "tests/test_tile_downloader.py",
    "tests/test_qt_worker_coverage.py",
    "tests/test_portal_registry.py",
    "tests/test_portal_live_smoke_matrix.py",
    "-q",
]

RELEASE_TESTS = [PYTHON, "-m", "pytest", "-q"]


def commands_for(profile: str) -> list[list[str]]:
    tests = SMOKE_TESTS if profile == "smoke" else RELEASE_TESTS
    return [*STATIC_CHECKS, COMPILE_CHECK, tests]


def run_gate(profile: str) -> int:
    commands = commands_for(profile)
    print(f"ATK-Pro quality gate: {profile} ({len(commands)} steps)")
    for index, command in enumerate(commands, 1):
        printable = subprocess.list2cmdline(command)
        print(f"[{index}/{len(commands)}] {printable}", flush=True)
        result = subprocess.run(command, cwd=ROOT, check=False)
        if result.returncode:
            print(f"FAILED at step {index}: {printable}", file=sys.stderr)
            return result.returncode
    print(f"ATK-Pro quality gate passed: {profile}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("profile", choices=("smoke", "release"))
    args = parser.parse_args()
    return run_gate(args.profile)


if __name__ == "__main__":
    raise SystemExit(main())
