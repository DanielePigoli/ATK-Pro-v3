from __future__ import annotations

import argparse
import csv
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.manifest_utils import (
    _PORTAL_BUILDERS,
    build_bnc_roma_synthetic_manifest,
    build_findbuch_synthetic_manifest,
    build_ia_synthetic_manifest,
    build_internetculturale_estense_synthetic_manifest,
    build_matricula_synthetic_manifest,
    build_museogalileo_synthetic_manifest,
    download_manifest,
    resolve_manifest_url,
    robust_find_manifest,
)
from src.portal_registry import PORTAL_REGISTRY, get_portal_referer, normalize_portal_key


DEFAULT_MATRIX = ROOT / "docs_generali" / "portal_live_smoke_samples.md"
DEFAULT_REPORT = ROOT / ".codex_tmp" / "portal_live_smoke_report.csv"
LIVE_SYNTHETIC_BUILDERS = {
    "bnc_roma": build_bnc_roma_synthetic_manifest,
    "findbuch": build_findbuch_synthetic_manifest,
    "internet_archive": build_ia_synthetic_manifest,
    "internetculturale_estense": build_internetculturale_estense_synthetic_manifest,
    "matricula": build_matricula_synthetic_manifest,
    "museogalileo": build_museogalileo_synthetic_manifest,
}


@dataclass(frozen=True)
class SmokeResult:
    portal_key: str
    label: str
    status: str
    sample_url: str
    manifest_url: str
    canvas_count: int
    detail: str


def _first(value: Any) -> str:
    if isinstance(value, str):
        return value
    if isinstance(value, list) and value:
        return _first(value[0])
    if isinstance(value, dict):
        for key in ("none", "it", "en", "de"):
            if key in value:
                return _first(value[key])
    return ""


def _canvas_count(manifest: Any) -> int:
    if not isinstance(manifest, dict):
        return 0

    sequences = manifest.get("sequences")
    if isinstance(sequences, list) and sequences:
        canvases = sequences[0].get("canvases")
        if isinstance(canvases, list):
            return len(canvases)

    items = manifest.get("items")
    if isinstance(items, list):
        return len(items)

    return 0


def _split_md_row(line: str) -> list[str]:
    return [cell.strip() for cell in line.strip().strip("|").split("|")]


def _read_markdown_matrix(path: Path) -> list[dict[str, str]]:
    rows = []
    headers: list[str] | None = None
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip().startswith("|"):
            continue
        cells = _split_md_row(line)
        if not cells:
            continue
        if all(set(cell.replace(":", "").strip()) <= {"-"} for cell in cells):
            continue
        if headers is None:
            headers = cells
            continue
        rows.append(dict(zip(headers, cells)))
    return rows


def _read_matrix(path: Path) -> list[dict[str, str]]:
    if path.suffix.lower() == ".csv":
        with path.open("r", encoding="utf-8-sig", newline="") as fh:
            return list(csv.DictReader(fh))
    return _read_markdown_matrix(path)


def _write_report(path: Path, results: list[SmokeResult]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(
            fh,
            fieldnames=[
                "portal_key",
                "label",
                "status",
                "sample_url",
                "manifest_url",
                "canvas_count",
                "detail",
            ],
        )
        writer.writeheader()
        for result in results:
            writer.writerow(result.__dict__)


def _download_or_probe_manifest(
    portal_key: str,
    sample_url: str,
    manifest_url: str,
    fetch_manifest: bool,
    output_dir: Path,
) -> tuple[str, int, str]:
    if not fetch_manifest:
        return "RESOLVED", 0, "Manifest URL resolved; remote manifest not fetched."

    referer = get_portal_referer(portal_key, sample_url)
    manifest = download_manifest(
        manifest_url,
        str(output_dir),
        titolo_doc=f"smoke_{portal_key}",
        referer=referer,
    )
    if manifest is None:
        return "FAIL", 0, "Manifest download failed or did not return JSON."

    count = _canvas_count(manifest)
    if count <= 0:
        return "FAIL", count, "Manifest fetched but no canvases/items were detected."
    return "PASS", count, "Manifest fetched and contains canvases/items."


def _resolve_without_remote_fetch(portal_key: str, sample_url: str) -> str | list | None:
    if portal_key == "manifest_diretto":
        return sample_url
    if portal_key == "antenati":
        return sample_url

    builder = _PORTAL_BUILDERS.get(portal_key)
    if not builder:
        return None
    return builder(sample_url)


def _resolve_with_remote_fetch(portal_key: str, sample_url: str) -> str | dict | list | None:
    if portal_key == "antenati":
        return robust_find_manifest(sample_url)

    synthetic_builder = LIVE_SYNTHETIC_BUILDERS.get(portal_key)
    if synthetic_builder:
        return synthetic_builder(sample_url)

    return resolve_manifest_url(sample_url, portal_key)


def run_case(row: dict[str, str], fetch_manifest: bool, output_dir: Path) -> SmokeResult:
    portal_key = normalize_portal_key(row.get("portal_key"))
    sample_url = (row.get("sample_url") or "").strip()
    label = row.get("label") or portal_key

    if portal_key not in PORTAL_REGISTRY:
        return SmokeResult(portal_key, label, "FAIL", sample_url, "", 0, "Unknown portal key.")

    if not sample_url or sample_url.upper().startswith("TODO"):
        return SmokeResult(
            portal_key,
            label,
            "TODO",
            sample_url,
            "",
            0,
            "Add a public no-login sample URL before release smoke verification.",
        )

    try:
        if not fetch_manifest:
            resolved = _resolve_without_remote_fetch(portal_key, sample_url)
            if resolved is None:
                return SmokeResult(portal_key, label, "FAIL", sample_url, "", 0, "Sample URL is not recognized by the portal builder.")
            if isinstance(resolved, list):
                resolved = next((item for item in resolved if item), "")
            return SmokeResult(
                portal_key,
                label,
                "RESOLVED",
                sample_url,
                str(resolved),
                0,
                "Sample URL configured and recognized; remote manifest not fetched.",
            )

        resolved = _resolve_with_remote_fetch(portal_key, sample_url)

        if resolved is None:
            return SmokeResult(portal_key, label, "FAIL", sample_url, "", 0, "No manifest resolved.")

        if isinstance(resolved, dict):
            count = _canvas_count(resolved)
            status = "PASS" if count > 0 else "FAIL"
            detail = "Synthetic manifest contains canvases/items." if count > 0 else "Synthetic manifest has no canvases/items."
            return SmokeResult(
                portal_key,
                label,
                status,
                sample_url,
                _first(resolved.get("@id") or resolved.get("id")),
                count,
                detail,
            )

        if isinstance(resolved, list):
            resolved = next((item for item in resolved if item), "")

        manifest_url = str(resolved)
        status, count, detail = _download_or_probe_manifest(
            portal_key,
            sample_url,
            manifest_url,
            fetch_manifest,
            output_dir,
        )
        return SmokeResult(portal_key, label, status, sample_url, manifest_url, count, detail)
    except Exception as exc:
        return SmokeResult(portal_key, label, "FAIL", sample_url, "", 0, f"{type(exc).__name__}: {exc}")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Release smoke verifier for ATK-Pro portal integrations."
    )
    parser.add_argument("--matrix", type=Path, default=DEFAULT_MATRIX)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    parser.add_argument("--output-dir", type=Path, default=ROOT / ".codex_tmp" / "portal_live_smoke")
    parser.add_argument(
        "--fetch-manifest",
        action="store_true",
        help="Fetch and validate remote manifests. Without this flag only manifest resolution is checked when possible.",
    )
    parser.add_argument("--only", action="append", default=[], help="Run only one portal key. Can be repeated.")
    parser.add_argument("--strict", action="store_true", help="Return exit code 1 when any filled sample fails or any portal is still TODO.")
    args = parser.parse_args()

    rows = _read_matrix(args.matrix)
    only = {normalize_portal_key(key) for key in args.only}
    if only:
        rows = [row for row in rows if normalize_portal_key(row.get("portal_key")) in only]

    results = [run_case(row, args.fetch_manifest, args.output_dir) for row in rows]
    _write_report(args.report, results)

    for result in results:
        suffix = f" ({result.canvas_count} canvases)" if result.canvas_count else ""
        print(f"{result.status:8} {result.portal_key:28} {result.detail}{suffix}")
    print(f"Report: {args.report}")

    if args.strict and any(result.status in {"FAIL", "TODO"} for result in results):
        return 1
    if any(result.status == "FAIL" for result in results):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
