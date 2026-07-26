from __future__ import annotations

from pathlib import Path
from urllib.parse import urlparse

from src.portal_registry import PORTAL_REGISTRY, detect_portal_from_url, portal_keys
import verify_portal_live_smoke as smoke


ROOT = Path(__file__).resolve().parents[1]
MATRIX = ROOT / "docs_generali" / "portal_live_smoke_samples.md"


def _rows() -> list[dict[str, str]]:
    rows = []
    headers = None
    for line in MATRIX.read_text(encoding="utf-8").splitlines():
        if not line.strip().startswith("|"):
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if all(set(cell.replace(":", "").strip()) <= {"-"} for cell in cells):
            continue
        if headers is None:
            headers = cells
            continue
        rows.append(dict(zip(headers, cells)))
    return rows


def test_live_smoke_matrix_covers_every_registered_portal():
    rows = _rows()
    keys = [row["portal_key"] for row in rows]
    assert keys == list(portal_keys())
    assert len(keys) == len(set(keys))


def test_live_smoke_matrix_repeats_registry_metadata():
    for row in _rows():
        portal = PORTAL_REGISTRY[row["portal_key"]]
        assert row["label"] == portal.label
        assert row["roadmap_priority"] == portal.roadmap_priority
        assert row["technical_family"] == portal.technical_family
        assert row["record_mode_policy"] == portal.record_mode_policy
        assert row["policy_checked_at"] == (portal.policy_checked_at or "per-request")


def test_live_smoke_matrix_rows_are_offline_resolvable(tmp_path):
    for row in _rows():
        result = smoke.run_case(row, fetch_manifest=False, output_dir=tmp_path)

        assert result.status == "RESOLVED", row["portal_key"]
        assert result.manifest_url, row["portal_key"]
        assert "recognized" in result.detail.lower(), row["portal_key"]


def test_live_smoke_matrix_offline_resolution_matches_technical_family(tmp_path):
    direct_families = {"iiif_direct", "iiif_discovery", "user_supplied_manifest"}
    synthetic_families = {"synthetic_manifest", "hybrid_manifest"}

    for row in _rows():
        portal_key = row["portal_key"]
        technical_family = row["technical_family"]
        result = smoke.run_case(row, fetch_manifest=False, output_dir=tmp_path)

        assert result.status == "RESOLVED", portal_key

        if technical_family in direct_families:
            assert isinstance(result.manifest_url, str)
            assert result.manifest_url
            assert not result.manifest_url.startswith("synthetic://"), portal_key
        elif technical_family in synthetic_families:
            assert isinstance(result.manifest_url, str)
            assert result.manifest_url
        else:
            raise AssertionError(f"Unexpected technical family for {portal_key}: {technical_family}")


def test_live_smoke_matrix_rows_keep_release_status_and_notes():
    allowed_statuses = {"SAMPLE", "TODO", "BLOCKED"}

    for row in _rows():
        assert row["release_status"] in allowed_statuses, row["portal_key"]
        assert row["notes"].strip(), row["portal_key"]


def test_live_smoke_matrix_sample_urls_are_absolute_and_match_detectable_hosts():
    allowed_aliases = {
        "memooria": {"brixiana", "memooria"},
        "manifest_diretto": {None},
    }

    for row in _rows():
        sample_url = row["sample_url"].strip()
        parsed = urlparse(sample_url)

        assert parsed.scheme in {"http", "https"}, row["portal_key"]
        assert parsed.netloc, row["portal_key"]
        assert " " not in sample_url, row["portal_key"]

        detected_portal = detect_portal_from_url(sample_url)
        allowed_detected = allowed_aliases.get(row["portal_key"])
        if allowed_detected is not None:
            assert detected_portal in allowed_detected, (row["portal_key"], detected_portal)
        elif detected_portal is not None:
            assert detected_portal == row["portal_key"], (row["portal_key"], detected_portal)


def test_live_smoke_matrix_duplicate_sample_urls_are_explicit():
    allowed_reuse = {
        "https://brixiana.jarvis.memooria.org/meta/iiif/a030f44e-9e0e-4d89-8e2f-c911df2ca1cc/manifest": {
            "brixiana",
            "memooria",
        }
    }
    seen_by_url: dict[str, set[str]] = {}

    for row in _rows():
        sample_url = row["sample_url"].strip()
        seen_by_url.setdefault(sample_url, set()).add(row["portal_key"])

    for sample_url, portal_keys_for_url in seen_by_url.items():
        if len(portal_keys_for_url) == 1:
            continue
        assert sample_url in allowed_reuse, sample_url
        assert portal_keys_for_url == allowed_reuse[sample_url], sample_url


def test_live_smoke_fetch_uses_synthetic_builder_for_synthetic_portals(monkeypatch, tmp_path):
    def fake_builder(sample_url: str) -> dict:
        assert sample_url == "https://bibdig.museogalileo.it/Teca/Viewer?an=000000006600"
        return {
            "@id": "synthetic://museogalileo/test",
            "sequences": [{"canvases": [{"@id": "canvas-1"}]}],
        }

    monkeypatch.setitem(smoke.LIVE_SYNTHETIC_BUILDERS, "museogalileo", fake_builder)

    result = smoke.run_case(
        {
            "portal_key": "museogalileo",
            "label": PORTAL_REGISTRY["museogalileo"].label,
            "sample_url": "https://bibdig.museogalileo.it/Teca/Viewer?an=000000006600",
        },
        fetch_manifest=True,
        output_dir=tmp_path,
    )

    assert result.status == "PASS"
    assert result.manifest_url == "synthetic://museogalileo/test"
    assert result.canvas_count == 1


def test_live_smoke_fetch_retries_transient_resolution_failure(monkeypatch, tmp_path):
    calls = {"count": 0}

    def flaky_builder(_sample_url: str):
        calls["count"] += 1
        if calls["count"] == 1:
            return None
        return {
            "@id": "synthetic://museogalileo/retry-ok",
            "sequences": [{"canvases": [{"@id": "canvas-1"}]}],
        }

    monkeypatch.setitem(smoke.LIVE_SYNTHETIC_BUILDERS, "museogalileo", flaky_builder)
    monkeypatch.setattr(smoke, "LIVE_FETCH_RETRY_DELAY_SECONDS", 0)

    result = smoke.run_case(
        {
            "portal_key": "museogalileo",
            "label": PORTAL_REGISTRY["museogalileo"].label,
            "sample_url": "https://bibdig.museogalileo.it/Teca/Viewer?an=000000006600",
        },
        fetch_manifest=True,
        output_dir=tmp_path,
    )

    assert result.status == "PASS"
    assert result.manifest_url == "synthetic://museogalileo/retry-ok"
    assert calls["count"] == 2
