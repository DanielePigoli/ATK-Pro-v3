from __future__ import annotations

from pathlib import Path

from src.portal_registry import PORTAL_REGISTRY, portal_keys


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
