#!/usr/bin/env python3
"""Verify pinned runtime dependencies and explicit Qt build configuration."""

from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parent
REQUIREMENTS = ROOT / "requirements.txt"
SPEC = ROOT / "ATK-Pro.spec"
WORKFLOWS = {
    "Windows": ROOT / ".github" / "workflows" / "build-windows.yml",
    "Linux": ROOT / ".github" / "workflows" / "build-linux.yml",
    "macOS": ROOT / ".github" / "workflows" / "build-macos.yml",
}
QT_MODULES = (
    "PySide6.QtCore",
    "PySide6.QtGui",
    "PySide6.QtWidgets",
    "PySide6.QtWebEngineWidgets",
)
CRITICAL_PINS = {
    "google-generativeai": "0.8.3",
    "openai": "2.33.0",
    "anthropic": "0.97.0",
    "google-auth": "2.45.0",
    "proto-plus": "1.27.0",
    "protobuf": "5.29.6",
    "pymupdf": "1.24.12",
    "pyside6[webengine]": "6.10.1",
    "pyinstaller": "6.16.0",
}


def fail(issues: list[str], condition: bool, message: str) -> None:
    if not condition:
        issues.append(message)


def main() -> int:
    issues: list[str] = []
    requirements = REQUIREMENTS.read_text(encoding="utf-8")
    spec = SPEC.read_text(encoding="utf-8")
    workflow_text = {name: path.read_text(encoding="utf-8") for name, path in WORKFLOWS.items()}

    parsed: dict[str, str] = {}
    for raw_line in requirements.splitlines():
        line = raw_line.split("#", 1)[0].strip()
        if not line:
            continue
        match = re.fullmatch(r"([^=<>!~\s]+)==([^\s]+)", line)
        fail(issues, match is not None, f"requirements.txt: dependency is not exactly pinned: {line}")
        if match:
            parsed[match.group(1).lower()] = match.group(2)

    for package, expected in CRITICAL_PINS.items():
        fail(
            issues,
            parsed.get(package) == expected,
            f"requirements.txt: expected {package}=={expected}, found {parsed.get(package)!r}",
        )

    fail(issues, "'PySide6'," not in spec, "ATK-Pro.spec: root PySide6 hidden import must not be forced")
    for module in QT_MODULES:
        fail(issues, f"'{module}'," in spec, f"ATK-Pro.spec: missing explicit hidden import {module}")

    for platform, text in workflow_text.items():
        fail(issues, "pip check" in text, f"{platform} workflow: pip check is missing")
        fail(issues, "pip freeze --all" in text, f"{platform} workflow: dependency inventory output is missing")

    for platform in ("Linux", "macOS"):
        text = workflow_text[platform]
        fail(
            issues,
            "--hidden-import=PySide6 \\" not in text,
            f"{platform} workflow: root PySide6 hidden import must not be forced",
        )
        expected_blocks = 2 if platform == "macOS" else 1
        for module in QT_MODULES:
            count = text.count(f"--hidden-import={module}")
            fail(
                issues,
                count == expected_blocks,
                f"{platform} workflow: expected {expected_blocks} explicit import(s) for {module}, found {count}",
            )

    if issues:
        print("Build reproducibility verification failed:")
        for issue in issues:
            print(f"- {issue}")
        return 1

    print("Build dependency pins and Qt module declarations are aligned.")
    print(f"- Exact requirements checked: {len(parsed)}")
    print("- Workflows checked: Windows, Linux, macOS Intel and Apple Silicon")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
