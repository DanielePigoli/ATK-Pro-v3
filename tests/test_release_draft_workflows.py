from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
UPLOAD_SCRIPT = ROOT / ".github" / "scripts" / "upload_release_assets.sh"
BUILD_WORKFLOWS = [
    ROOT / ".github" / "workflows" / "build-windows.yml",
    ROOT / ".github" / "workflows" / "build-linux.yml",
    ROOT / ".github" / "workflows" / "build-macos.yml",
]
SMOKE_WORKFLOWS = [
    ROOT / ".github" / "workflows" / "smoke-windows-installer.yml",
    ROOT / ".github" / "workflows" / "smoke-linux-release.yml",
    ROOT / ".github" / "workflows" / "smoke-macos-release.yml",
]


def test_release_uploader_preserves_existing_draft_state():
    script = UPLOAD_SCRIPT.read_text(encoding="utf-8")

    assert "uploads.github.com/repos/$repo/releases/$release_id/assets" in script
    assert "release_is_draft" in script
    assert r'select(.tag_name == \"$tag\")' in script
    assert r'select(.name == \"$asset_name\")' in script
    assert '--upload-file "$asset_path"' in script
    assert "--data-binary" not in script
    assert "--field draft=false" not in script
    assert 'gh api --method DELETE "repos/$repo/releases/assets/$existing_id"' in script


def test_build_workflows_use_draft_safe_uploader():
    combined = "\n".join(path.read_text(encoding="utf-8") for path in BUILD_WORKFLOWS)

    assert combined.count("bash .github/scripts/upload_release_assets.sh") == 4
    assert "--field draft=false" not in combined
    assert "gh release upload" not in combined


def test_macos_workflow_can_rebuild_one_architecture_from_an_exact_release_ref():
    workflow = BUILD_WORKFLOWS[-1].read_text(encoding="utf-8")

    assert "source_ref:" in workflow
    assert "build_target:" in workflow
    assert "ref: ${{ inputs.source_ref || github.ref }}" in workflow
    assert "inputs.build_target == 'intel'" in workflow
    assert "inputs.build_target == 'silicon'" in workflow
    assert "inputs.source_ref || github.ref_name" in workflow


def test_macos_intel_dmg_has_non_mounting_fallback_and_is_verified():
    workflow = BUILD_WORKFLOWS[-1].read_text(encoding="utf-8")

    assert "create-dmg non ha completato lo smontaggio" in workflow
    assert "-format UDZO" in workflow
    assert "-srcfolder dist/dmg_intel" in workflow
    assert 'hdiutil verify "dist/${DMG_NAME}"' in workflow


def test_release_smokes_download_assets_through_authenticated_api():
    for workflow in SMOKE_WORKFLOWS:
        text = workflow.read_text(encoding="utf-8")
        assert "actions: read" in text
        assert "contents: read" in text
        assert "contents: write" not in text
        assert "build_run_id:" in text
        assert "gh run download" in text
        assert "releases?per_page=100" in text
        assert "Accept: application/octet-stream" in text
        assert "gh release download" not in text


def test_windows_smoke_stops_all_matching_app_processes_before_uninstall():
    workflow = SMOKE_WORKFLOWS[0].read_text(encoding="utf-8")

    assert workflow.count("Get-CimInstance Win32_Process -Filter \"Name='ATK-Pro.exe'\"") >= 6
    assert workflow.count("Equals($exePath, [StringComparison]::OrdinalIgnoreCase)") >= 4
    assert "Installed smoke left an ATK-Pro process running." in workflow
