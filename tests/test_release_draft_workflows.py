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


def test_release_smokes_download_assets_through_authenticated_api():
    for workflow in SMOKE_WORKFLOWS:
        text = workflow.read_text(encoding="utf-8")
        assert "releases?per_page=100" in text
        assert "Accept: application/octet-stream" in text
        assert "gh release download" not in text
