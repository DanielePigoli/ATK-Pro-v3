from __future__ import annotations

import argparse
import csv
import hashlib
from io import BytesIO
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import requests
from PIL import Image


ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.manifest_utils import (
    _PORTAL_BUILDERS,
    build_biblioteca_digitale_lombarda_synthetic_manifest,
    build_biblioteca_digitale_trentina_synthetic_manifest,
    build_bnc_roma_synthetic_manifest,
    build_doge_synthetic_manifest,
    build_findbuch_synthetic_manifest,
    build_ia_synthetic_manifest,
    build_internetculturale_estense_synthetic_manifest,
    build_matricula_synthetic_manifest,
    build_museogalileo_synthetic_manifest,
    build_rovereto_synthetic_manifest,
    download_manifest,
    resolve_manifest_url,
    robust_find_manifest,
)
from src.portal_adapters import resolve_direct_image_download
from src.portal_registry import PORTAL_REGISTRY, get_portal_referer, normalize_portal_key
from src.tile_downloader import _headers_for_tile_url


DEFAULT_MATRIX = ROOT / "docs_generali" / "portal_live_smoke_samples.md"
DEFAULT_REPORT = ROOT / ".codex_tmp" / "portal_live_smoke_report.csv"
LIVE_FETCH_ATTEMPTS = 3
LIVE_FETCH_RETRY_DELAY_SECONDS = 2
LIVE_SYNTHETIC_BUILDERS = {
    "biblioteca_digitale_lombarda": build_biblioteca_digitale_lombarda_synthetic_manifest,
    "biblioteca_digitale_trentina": build_biblioteca_digitale_trentina_synthetic_manifest,
    "bnc_roma": build_bnc_roma_synthetic_manifest,
    "doge_unige": build_doge_synthetic_manifest,
    "findbuch": build_findbuch_synthetic_manifest,
    "internet_archive": build_ia_synthetic_manifest,
    "internetculturale_estense": build_internetculturale_estense_synthetic_manifest,
    "matricula": build_matricula_synthetic_manifest,
    "museogalileo": build_museogalileo_synthetic_manifest,
    "rovereto_digital_library": build_rovereto_synthetic_manifest,
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
    sampled_images: int = 0
    unique_images: int = 0
    image_detail: str = ""


@dataclass(frozen=True)
class ImageProbe:
    position: int
    status: str
    width: int
    height: int
    byte_count: int
    sha256: str
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


def _canvases(manifest: Any) -> list[dict]:
    if not isinstance(manifest, dict):
        return []
    sequences = manifest.get("sequences")
    if isinstance(sequences, list) and sequences:
        canvases = sequences[0].get("canvases")
        if isinstance(canvases, list):
            return [canvas for canvas in canvases if isinstance(canvas, dict)]
    return []


def _sample_positions(canvas_count: int, sample_count: int) -> list[int]:
    if canvas_count <= 0 or sample_count <= 0:
        return []
    if canvas_count <= sample_count:
        return list(range(canvas_count))
    if sample_count == 1:
        return [0]
    return sorted({round(index * (canvas_count - 1) / (sample_count - 1)) for index in range(sample_count)})


def _canvas_resource_and_service(canvas: dict) -> tuple[dict, dict, str]:
    images = canvas.get("images") or []
    resource = images[0].get("resource") if images and isinstance(images[0], dict) else {}
    resource = resource if isinstance(resource, dict) else {}
    service = resource.get("service") or {}
    if isinstance(service, list):
        service = next((item for item in service if isinstance(item, dict)), {})
    service = service if isinstance(service, dict) else {}
    service_id = str(service.get("@id") or service.get("id") or "").strip()
    return resource, service, service_id


def _measure_image(position: int, image: Image.Image, byte_count: int, detail: str) -> ImageProbe:
    image.load()
    width, height = image.size
    if width <= 1 or height <= 1:
        raise ValueError(f"invalid dimensions {width}x{height}")
    normalized = image.convert("RGB")
    try:
        pixel_hash = hashlib.sha256(normalized.tobytes()).hexdigest()
    finally:
        normalized.close()
    return ImageProbe(position, "PASS", width, height, byte_count, pixel_hash, detail)


def _decode_image(position: int, content: bytes, detail: str) -> ImageProbe:
    try:
        with Image.open(BytesIO(content)) as image:
            return _measure_image(position, image, len(content), detail)
    except Exception as exc:
        return ImageProbe(position, "FAIL", 0, 0, len(content), "", f"{detail}: invalid image ({exc})")


def _request_image(
    position: int,
    url: str,
    referer: str | None,
    *,
    session: requests.Session | None = None,
    params: dict[str, Any] | None = None,
) -> ImageProbe:
    headers = _headers_for_tile_url(url, referer=referer)
    headers["Accept"] = "image/jpeg,image/png,image/*;q=0.9,*/*;q=0.8"
    client = session or requests
    last_detail = url
    for attempt in range(1, LIVE_FETCH_ATTEMPTS + 1):
        try:
            response = client.get(url, headers=headers, params=params, timeout=60)
            last_detail = f"HTTP {response.status_code} {response.url}"
            if response.ok and response.content:
                probe = _decode_image(position, response.content, last_detail)
                if probe.status == "PASS":
                    return probe
        except Exception as exc:
            last_detail = f"{type(exc).__name__}: {exc} ({url})"
        if attempt < LIVE_FETCH_ATTEMPTS:
            time.sleep(LIVE_FETCH_RETRY_DELAY_SECONDS)
    return ImageProbe(position, "FAIL", 0, 0, 0, "", last_detail)


def _probe_findbuch_image(position: int, service: dict) -> ImageProbe:
    try:
        base_url = str(service["base_url"])
        view_url = str(service["view_url"])
        session = requests.Session()
        headers = {"User-Agent": "Mozilla/5.0", "Accept": "text/html,application/xhtml+xml,*/*;q=0.8"}
        session.get(base_url + "main.php", headers=headers, timeout=20)
        session.get(view_url, headers={**headers, "Referer": base_url + "main.php"}, timeout=20)
        return _request_image(
            position,
            base_url + "gtpc.php",
            view_url,
            session=session,
            params={"be_id": service["be_id"], "ve_id": service["ve_id"], "count": service["count"]},
        )
    except Exception as exc:
        return ImageProbe(position, "FAIL", 0, 0, 0, "", f"Findbuch setup failed: {exc}")


def _probe_canvas_image(portal_key: str, sample_url: str, canvas: dict, position: int) -> ImageProbe:
    resource, service, service_id = _canvas_resource_and_service(canvas)
    resource_id = str(resource.get("@id") or resource.get("id") or "").strip()
    context = str(service.get("@context") or "")
    referer = get_portal_referer(portal_key, sample_url)

    direct_adapter, direct_url = resolve_direct_image_download(portal_key, canvas, service_id or None)
    if direct_adapter and direct_url:
        image, status, byte_count = direct_adapter.download_image(direct_url)
        if image is None:
            return ImageProbe(position, "FAIL", 0, 0, byte_count, "", f"HTTP {status} {direct_url}")
        try:
            return _measure_image(position, image, byte_count, f"direct adapter {direct_url}")
        except Exception as exc:
            return ImageProbe(position, "FAIL", 0, 0, byte_count, "", f"{direct_url}: invalid image ({exc})")

    if context == "findbuch_gtpc":
        return _probe_findbuch_image(position, service)

    if service_id and "ImageViewer/servlet/ImageViewer" in service_id and "azione=showImg" in service_id:
        return _request_image(position, service_id, referer)

    if service_id:
        image_context = context.lower()
        quality = "native" if "/image/1/" in image_context else "default"
        candidates = [f"{service_id.rstrip('/')}/full/512,/0/{quality}.jpg"]
        if quality != "default":
            candidates.append(f"{service_id.rstrip('/')}/full/512,/0/default.jpg")
        for candidate in candidates:
            probe = _request_image(position, candidate, referer)
            if probe.status == "PASS":
                return probe

    if resource_id.startswith(("http://", "https://")):
        return _request_image(position, resource_id, referer)
    return ImageProbe(position, "FAIL", 0, 0, 0, "", "Canvas has no downloadable image URL.")


def _probe_manifest_images(
    portal_key: str,
    sample_url: str,
    manifest: dict,
    sample_count: int,
) -> tuple[str, int, int, str]:
    canvases = _canvases(manifest)
    positions = _sample_positions(len(canvases), sample_count)
    probes = [_probe_canvas_image(portal_key, sample_url, canvases[position], position + 1) for position in positions]
    failures = [probe for probe in probes if probe.status == "FAIL"]
    hashes = [probe.sha256 for probe in probes if probe.sha256]
    unique_count = len(set(hashes))
    summaries = [
        f"p{probe.position}:{probe.status}:{probe.width}x{probe.height}:{probe.byte_count}B:{probe.sha256[:12]}"
        for probe in probes
    ]
    if failures:
        failed = "; ".join(f"p{probe.position} {probe.detail}" for probe in failures)
        return "FAIL", len(probes) - len(failures), unique_count, f"{' | '.join(summaries)}; failures: {failed}"
    if len(probes) > 1 and unique_count == 1:
        return "FAIL", len(probes), unique_count, f"{' | '.join(summaries)}; all sampled images are byte-identical"
    if len(probes) > 2 and unique_count < len(probes):
        return "WARN", len(probes), unique_count, f"{' | '.join(summaries)}; repeated sampled image detected"
    return "PASS", len(probes), unique_count, " | ".join(summaries)


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
                "sampled_images",
                "unique_images",
                "image_detail",
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
) -> tuple[str, int, str, dict | None]:
    if not fetch_manifest:
        return "RESOLVED", 0, "Manifest URL resolved; remote manifest not fetched.", None

    referer = get_portal_referer(portal_key, sample_url)
    manifest = download_manifest(
        manifest_url,
        str(output_dir),
        titolo_doc=f"smoke_{portal_key}",
        referer=referer,
    )
    if manifest is None:
        return "FAIL", 0, "Manifest download failed or did not return JSON.", None

    count = _canvas_count(manifest)
    if count <= 0:
        return "FAIL", count, "Manifest fetched but no canvases/items were detected.", manifest
    return "PASS", count, "Manifest fetched and contains canvases/items.", manifest


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


def _resolve_with_remote_fetch_retries(portal_key: str, sample_url: str) -> tuple[str | dict | list | None, int]:
    for attempt in range(1, LIVE_FETCH_ATTEMPTS + 1):
        resolved = _resolve_with_remote_fetch(portal_key, sample_url)
        if resolved is not None:
            return resolved, attempt
        if attempt < LIVE_FETCH_ATTEMPTS:
            time.sleep(LIVE_FETCH_RETRY_DELAY_SECONDS)
    return None, LIVE_FETCH_ATTEMPTS


def run_case(
    row: dict[str, str],
    fetch_manifest: bool,
    output_dir: Path,
    *,
    fetch_images: bool = False,
    image_samples: int = 3,
) -> SmokeResult:
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
        if not fetch_manifest and not fetch_images:
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

        resolved, attempts = _resolve_with_remote_fetch_retries(portal_key, sample_url)

        if resolved is None:
            return SmokeResult(portal_key, label, "FAIL", sample_url, "", 0, f"No manifest resolved after {attempts} attempts.")

        manifest = resolved if isinstance(resolved, dict) else None
        if manifest is not None:
            count = _canvas_count(manifest)
            status = "PASS" if count > 0 else "FAIL"
            detail = "Synthetic manifest contains canvases/items." if count > 0 else "Synthetic manifest has no canvases/items."
            manifest_url = _first(manifest.get("@id") or manifest.get("id"))
        else:
            if isinstance(resolved, list):
                resolved = next((item for item in resolved if item), "")
            manifest_url = str(resolved)
            status, count, detail, manifest = _download_or_probe_manifest(
                portal_key,
                sample_url,
                manifest_url,
                True,
                output_dir,
            )

        if status != "PASS" or not fetch_images:
            return SmokeResult(portal_key, label, status, sample_url, manifest_url, count, detail)

        image_status, sampled_images, unique_images, image_detail = _probe_manifest_images(
            portal_key,
            sample_url,
            manifest or {},
            image_samples,
        )
        return SmokeResult(
            portal_key,
            label,
            image_status,
            sample_url,
            manifest_url,
            count,
            detail,
            sampled_images,
            unique_images,
            image_detail,
        )
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
    parser.add_argument(
        "--fetch-images",
        action="store_true",
        help="Fetch and decode representative images from evenly spaced canvases; implies --fetch-manifest.",
    )
    parser.add_argument(
        "--image-samples",
        type=int,
        default=3,
        help="Number of evenly spaced canvas images to probe (default: 3).",
    )
    parser.add_argument("--only", action="append", default=[], help="Run only one portal key. Can be repeated.")
    parser.add_argument("--strict", action="store_true", help="Return exit code 1 when any filled sample fails or any portal is still TODO.")
    args = parser.parse_args()

    rows = _read_matrix(args.matrix)
    only = {normalize_portal_key(key) for key in args.only}
    if only:
        rows = [row for row in rows if normalize_portal_key(row.get("portal_key")) in only]

    if args.image_samples < 1:
        parser.error("--image-samples must be at least 1")
    results = [
        run_case(
            row,
            args.fetch_manifest or args.fetch_images,
            args.output_dir,
            fetch_images=args.fetch_images,
            image_samples=args.image_samples,
        )
        for row in rows
    ]
    _write_report(args.report, results)

    for result in results:
        suffix = f" ({result.canvas_count} canvases)" if result.canvas_count else ""
        print(f"{result.status:8} {result.portal_key:28} {result.detail}{suffix}")
        if result.image_detail:
            print(f"{'':8} {'':28} {result.image_detail}")
    print(f"Report: {args.report}")

    if args.strict and any(result.status in {"FAIL", "TODO", "WARN"} for result in results):
        return 1
    if any(result.status == "FAIL" for result in results):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
