from __future__ import annotations

from pathlib import Path

from src.portal_registry import PORTAL_REGISTRY, portal_keys
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
