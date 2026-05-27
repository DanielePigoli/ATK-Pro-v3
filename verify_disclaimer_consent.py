#!/usr/bin/env python3
"""Verify v3 legal disclaimer acceptance gates across packaged builds."""

from __future__ import annotations

import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent
DISCLAIMER_REVISION = "v3.0.0-legal-disclaimer-2026-05-27"

FILES = {
    "main_gui": ROOT / "src" / "main_gui_qt.py",
    "inno": ROOT / "ATK-Pro-Installer.iss",
    "deb_config": ROOT / ".github" / "deb-scripts" / "config",
    "deb_preinst": ROOT / ".github" / "deb-scripts" / "preinst",
    "deb_postinst": ROOT / ".github" / "deb-scripts" / "postinst",
    "deb_templates": ROOT / ".github" / "deb-scripts" / "templates",
    "linux_workflow": ROOT / ".github" / "workflows" / "build-linux.yml",
    "macos_workflow": ROOT / ".github" / "workflows" / "build-macos.yml",
}


def read(name: str) -> str:
    path = FILES[name]
    if not path.is_file():
        raise FileNotFoundError(path)
    return path.read_text(encoding="utf-8", errors="replace")


def require(issues: list[str], condition: bool, message: str) -> None:
    if not condition:
        issues.append(message)


def main() -> int:
    issues: list[str] = []

    main_gui = read("main_gui")
    inno = read("inno")
    deb_config = read("deb_config")
    deb_preinst = read("deb_preinst")
    deb_postinst = read("deb_postinst")
    deb_templates = read("deb_templates")
    linux_workflow = read("linux_workflow")
    macos_workflow = read("macos_workflow")

    for name, text in {
        "src/main_gui_qt.py": main_gui,
        "ATK-Pro-Installer.iss": inno,
        ".github/deb-scripts/config": deb_config,
        ".github/deb-scripts/preinst": deb_preinst,
        ".github/deb-scripts/postinst": deb_postinst,
    }.items():
        require(issues, DISCLAIMER_REVISION in text, f"{name}: missing disclaimer revision {DISCLAIMER_REVISION}")

    require(issues, 'GITHUB_REPO = "DanielePigoli/ATK-Pro-v3"' in main_gui, "main_gui_qt.py: update checker must target ATK-Pro-v3")
    require(issues, 'DISCLAIMER_SOURCE_LANGUAGE = "it"' in main_gui, "main_gui_qt.py: current legal disclaimer source must be Italian")
    require(issues, "_is_current_disclaimer_accepted()" in main_gui, "main_gui_qt.py: missing revisioned disclaimer acceptance check")
    require(issues, "DISCLAIMER_ACCEPT_PARAM" in main_gui, "main_gui_qt.py: update installer must pass disclaimer acceptance parameter")
    require(issues, "DISCLAIMER_ACCEPT_PARAM])" in main_gui, "main_gui_qt.py: silent updater does not pass disclaimer acceptance parameter")
    require(issues, "_load_current_disclaimer_text()" in main_gui, "main_gui_qt.py: acceptance dialog must load the current canonical disclaimer")
    require(issues, "window.show()" in main_gui, "main_gui_qt.py: expected main window startup marker missing")

    disclaimer_check_pos = main_gui.find("not _is_current_disclaimer_accepted()")
    window_show_pos = main_gui.find("window.show()")
    require(
        issues,
        disclaimer_check_pos != -1 and window_show_pos != -1 and disclaimer_check_pos < window_show_pos,
        "main_gui_qt.py: disclaimer acceptance must be checked before showing the main window",
    )

    require(issues, "#define MyDisclaimerRevision" in inno, "Inno installer: missing disclaimer revision define")
    require(issues, "HasDisclaimerAcceptanceParam" in inno, "Inno installer: missing silent acceptance parameter check")
    require(issues, "WizardSilent" in inno, "Inno installer: silent installs must be guarded")
    require(issues, "ShouldSkipPage" in inno and "wpLicense" in inno, "Inno installer: license page skip must be revision-aware")
    require(issues, "DisclaimerRevision" in inno, "Inno installer: accepted disclaimer revision must be persisted")
    require(issues, 'LicenseFile: "assets\\it\\testuali\\disclaimer_legale_ATK-Pro.txt"' in inno,
            "Inno installer: installer must show the current Italian legal disclaimer")
    require(issues, 'LicenseFile: "assets\\en\\testuali\\disclaimer_legale_ATK-Pro.txt"' not in inno,
            "Inno installer: must not show stale localized legal disclaimers for v3 acceptance")

    require(issues, 'if [ "$1" = "install" ] || {' in deb_config, "Debian config: upgrade must ask again when revision changed")
    require(issues, '_NEEDS_DISCLAIMER=1' in deb_preinst, "Debian preinst: missing revision-based disclaimer gate")
    require(issues, 'elif [ "$1" = "upgrade" ] && [ "$_CURRENT_DISCLAIMER_REVISION" != "$DISCLAIMER_REVISION" ]; then' in deb_preinst,
            "Debian preinst: upgrade must require acceptance when revision changed")
    require(issues, "installation cancelled because the legal disclaimer was not accepted" in deb_preinst,
            "Debian preinst: missing hard stop when disclaimer cannot be accepted")
    require(issues, "touch /var/lib/atk-pro/pending-disclaimer" not in deb_preinst,
            "Debian preinst: must not install and defer acceptance with pending flag")
    require(issues, '_DISC_TAG="Description:"' in deb_preinst,
            "Debian preinst: zenity fallback must load the canonical legal disclaimer")
    require(issues, "disclaimer_revision" in deb_postinst, "Debian postinst: accepted revision must be persisted")
    require(issues, "Version 2.0" not in deb_templates and "Versione 2.0" not in deb_templates,
            "Debian templates: stale v2 disclaimer text must not be shown")
    require(issues, "portali genealogici commerciali" in deb_templates and "risorse documentarie o archivistiche di terzi" in deb_templates,
            "Debian templates: current v3 legal disclaimer content is missing")
    require(issues, "Description-it: Accettare il Disclaimer" not in deb_templates,
            "Debian templates: translated stale disclaimer sections must not override the canonical text")

    require(issues, "--eula /tmp/atk-disclaimer.txt" in macos_workflow,
            "macOS workflow: DMG must include disclaimer EULA")
    require(issues, "cp assets/it/testuali/disclaimer_legale_ATK-Pro.txt /tmp/atk-disclaimer.txt" in macos_workflow,
            "macOS workflow: DMG EULA must use the current Italian legal disclaimer")
    require(issues, "cp assets/en/testuali/disclaimer_legale_ATK-Pro.txt /tmp/atk-disclaimer.txt" not in macos_workflow,
            "macOS workflow: DMG must not use stale English legal disclaimer")
    require(issues, "ATK-Pro-Linux.tar.gz" in linux_workflow and "ATK-Pro-Linux.deb" in linux_workflow,
            "Linux workflow: expected tarball and DEB packaging outputs are missing")

    old_repo_hits = [
        match.group(0)
        for match in re.finditer(
            r"ATK-Pro-v2",
            main_gui + inno + deb_preinst + deb_templates + linux_workflow + macos_workflow,
        )
    ]
    require(issues, not old_repo_hits, "v3 release/update paths must not reference ATK-Pro-v2")

    if issues:
        print("Disclaimer consent verification failed:")
        for issue in issues:
            print(f"- {issue}")
        return 1

    print("Disclaimer consent gates are aligned.")
    print(f"- Revision: {DISCLAIMER_REVISION}")
    print("- Checked: app startup, Windows installer, Debian scripts, Linux packages, macOS DMG workflow")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except FileNotFoundError as exc:
        print(f"Missing file: {exc}", file=sys.stderr)
        raise SystemExit(1)
