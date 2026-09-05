from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
DEB_SCRIPTS = ROOT / ".github" / "deb-scripts"
BUILD_WORKFLOW = ROOT / ".github" / "workflows" / "build-linux.yml"
SMOKE_WORKFLOW = ROOT / ".github" / "workflows" / "smoke-linux-release.yml"


def test_postrm_removes_only_system_state_on_purge() -> None:
    script = (DEB_SCRIPTS / "postrm").read_text(encoding="utf-8")

    assert 'if [ "$1" = "purge" ]; then' in script
    assert "/etc/atk-pro/disclaimer_revision" in script
    assert "/etc/atk-pro/defaults.json" in script
    assert "rmdir /etc/atk-pro" in script
    assert "db_purge" in script
    assert "rm -rf" not in script
    assert "/home/" not in script


def test_linux_build_embeds_and_enables_postrm() -> None:
    workflow = BUILD_WORKFLOW.read_text(encoding="utf-8")

    assert 'cp .github/deb-scripts/postrm' in workflow
    assert '"$PKG_DIR/DEBIAN/postrm"' in workflow
    assert "postinst, prerm, postrm" in workflow


def test_postrm_has_valid_posix_shell_syntax() -> None:
    shell = shutil.which("sh")
    if shell is None:
        pytest.skip("POSIX sh is not available on this platform")

    subprocess.run(
        [shell, "-n", str(DEB_SCRIPTS / "postrm")],
        check=True,
        capture_output=True,
        text=True,
    )



def test_linux_smoke_can_validate_fresh_build_artifacts() -> None:
    workflow = SMOKE_WORKFLOW.read_text(encoding="utf-8")

    assert "build_run_id:" in workflow
    assert 'gh run download "$BUILD_RUN_ID"' in workflow
    assert '--name "ATK-Pro-Linux-deb"' in workflow
    assert '--name "ATK-Pro-Linux-tarball"' in workflow
