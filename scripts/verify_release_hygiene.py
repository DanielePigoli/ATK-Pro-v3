#!/usr/bin/env python3
"""Audit release hygiene without deleting local development artifacts."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
GENERATED_DIRS = {
    "__pycache__",
    ".pytest_cache",
    ".codex_tmp",
    "_win_artifacts",
    "build",
    "dist",
    "out",
    "outdir",
    "output",
    "outputs",
    "scratch",
    "tmp",
}
GENERATED_SUFFIXES = {
    ".bak",
    ".dmg",
    ".log",
    ".pyc",
    ".sarif",
    ".tmp",
    ".zip",
}
GENERATED_NAMES = {
    "localization_check_report.txt",
    "portal_policy_overrides.json",
    "portable.txt",
}


def _git_lines(*args: str) -> list[str]:
    result = subprocess.run(
        ["git", *args],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    return [line.strip().replace("\\", "/") for line in result.stdout.splitlines() if line.strip()]


def _looks_generated(path_text: str) -> bool:
    path = Path(path_text)
    parts = {part.lower() for part in path.parts}
    name = path.name.lower()
    return bool(
        parts & GENERATED_DIRS
        or path.suffix.lower() in GENERATED_SUFFIXES
        or name in GENERATED_NAMES
        or name.startswith(("atkpro_debug.log", "atkpro_output.log"))
    )


def audit_release_hygiene() -> tuple[list[str], list[str], list[str]]:
    tracked_generated = sorted(path for path in _git_lines("ls-files") if _looks_generated(path))
    unignored_generated = sorted(
        path
        for path in _git_lines("ls-files", "--others", "--exclude-standard")
        if _looks_generated(path)
    )
    ignored_generated = sorted(
        path
        for path in _git_lines("ls-files", "--others", "--ignored", "--exclude-standard")
        if _looks_generated(path)
    )
    return tracked_generated, unignored_generated, ignored_generated


def main() -> int:
    try:
        tracked, unignored, ignored = audit_release_hygiene()
    except (OSError, subprocess.CalledProcessError) as exc:
        print(f"ERROR: release hygiene audit failed: {exc}", file=sys.stderr)
        return 2

    print(f"Ignored generated artifacts inventoried: {len(ignored)}")
    if tracked:
        print("ERROR: generated artifacts tracked by Git:", file=sys.stderr)
        for path in tracked:
            print(f"- {path}", file=sys.stderr)
    if unignored:
        print("ERROR: generated artifacts not covered by .gitignore:", file=sys.stderr)
        for path in unignored:
            print(f"- {path}", file=sys.stderr)

    if tracked or unignored:
        return 1
    print("Release hygiene audit passed: no generated artifact can enter a commit.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
