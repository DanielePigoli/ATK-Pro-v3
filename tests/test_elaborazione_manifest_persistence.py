import json

from src.elaborazione import Elaborazione


def test_set_manifest_location_updates_runtime_paths(tmp_path):
    elab = Elaborazione("D", "https://example.test/item/1", str(tmp_path))

    manifest_path = elab._set_manifest_location(str(tmp_path / "work"), "manifest_test.json")

    assert manifest_path == str(tmp_path / "work" / "manifest_test.json")
    assert elab.manifest_path == manifest_path
    assert elab.output_dir == str(tmp_path / "work")


def test_save_manifest_json_writes_file_and_updates_runtime_paths(tmp_path):
    elab = Elaborazione("R", "https://example.test/item/2", str(tmp_path))
    manifest = {"sequences": [{"canvases": [{"label": "1"}]}]}

    manifest_path = elab._save_manifest_json(
        manifest,
        str(tmp_path / "work"),
        "manifest_test.json",
    )

    assert elab.manifest_path == manifest_path
    assert elab.output_dir == str(tmp_path / "work")
    saved = json.loads((tmp_path / "work" / "manifest_test.json").read_text(encoding="utf-8"))
    assert saved == manifest
