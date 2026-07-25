from __future__ import annotations

import verify_manifest_url as probe


def test_canvas_count_counts_iiif_v2_canvases():
    manifest = {"sequences": [{"canvases": [{}, {}, {}]}]}

    assert probe.canvas_count(manifest) == 3


def test_canvas_count_counts_iiif_v3_items():
    manifest = {"items": [{}, {}]}

    assert probe.canvas_count(manifest) == 2


def test_canvas_count_returns_zero_for_missing_or_invalid_manifest():
    assert probe.canvas_count({}) == 0
    assert probe.canvas_count(None) == 0


def test_child_manifest_count_counts_iiif_v2_collection_manifests():
    manifest = {"manifests": [{}, {}, {}]}

    assert probe.child_manifest_count(manifest) == 3


def test_classify_manifest_prefers_canvas_items_over_child_manifests():
    manifest = {
        "sequences": [{"canvases": [{}, {}]}],
        "manifests": [{}, {}, {}],
    }

    assert probe.classify_manifest(manifest) == ("canvas", 2)


def test_classify_manifest_accepts_collection_with_child_manifests():
    manifest = {"@type": "sc:Collection", "manifests": [{}, {}]}

    assert probe.classify_manifest(manifest) == ("collection", 2)


def test_main_reports_success_for_manifest_with_canvases(monkeypatch, tmp_path, capsys):
    monkeypatch.setattr(probe, "download_manifest", lambda *args, **kwargs: {"sequences": [{"canvases": [{}]}]})

    result = probe.main(
        [
            "--url",
            "https://example.test/manifest.json",
            "--output-dir",
            str(tmp_path),
        ]
    )

    assert result == 0
    assert "PASS Manifest scaricato e valido. Canvas/items: 1" in capsys.readouterr().out


def test_main_reports_failure_for_missing_manifest(monkeypatch, tmp_path, capsys):
    monkeypatch.setattr(probe, "download_manifest", lambda *args, **kwargs: None)

    result = probe.main(
        [
            "--url",
            "https://example.test/manifest.json",
            "--output-dir",
            str(tmp_path),
        ]
    )

    assert result == 1
    assert "FAIL Manifest non scaricato o non valido." in capsys.readouterr().out


def test_main_reports_success_for_collection_with_child_manifests(monkeypatch, tmp_path, capsys):
    monkeypatch.setattr(
        probe,
        "download_manifest",
        lambda *args, **kwargs: {"@type": "sc:Collection", "manifests": [{}, {}, {}]},
    )

    result = probe.main(
        [
            "--url",
            "https://example.test/collection.json",
            "--output-dir",
            str(tmp_path),
        ]
    )

    assert result == 0
    assert "PASS Collection IIIF scaricata e valida. Manifest figli: 3" in capsys.readouterr().out
