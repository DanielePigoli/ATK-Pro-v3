"""Preflight riproducibile dei percorsi materializzati da ATK-Pro.

Il modulo non modifica mai i nomi dell'utente. Distingue violazioni hard
documentate da indicatori prudenziali, così che i chiamanti possano bloccare
solo le prime e presentare separatamente i secondi.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import PureWindowsPath
import os
import re
from urllib.parse import quote


INVALID_WINDOWS_CHARS = frozenset('<>:"/\\|?*')
RESERVED_WINDOWS_NAMES = frozenset(
    {"CON", "PRN", "AUX", "NUL"}
    | {f"COM{i}" for i in range(1, 10)}
    | {f"LPT{i}" for i in range(1, 10)}
)


@dataclass(frozen=True)
class TargetProfile:
    name: str
    max_segment: int = 255
    max_absolute: int | None = None
    max_cloud_relative: int | None = None
    max_onedrive_sync: int | None = None
    warning_ratio: float = 0.90


WINDOWS_DESKTOP = TargetProfile("windows_desktop", max_absolute=260)
MODERN_FILESYSTEM = TargetProfile("modern_filesystem")
ONEDRIVE = TargetProfile(
    "onedrive_sharepoint",
    max_cloud_relative=400,
    max_onedrive_sync=520,
)


@dataclass(frozen=True)
class PathMetrics:
    path: str
    absolute_local: int
    cloud_relative: int | None
    encoded_risk: int | None
    max_segment: int


@dataclass(frozen=True)
class PathIssue:
    severity: str
    code: str
    path: str
    metric: int | str
    limit: int | str
    message: str


@dataclass(frozen=True)
class PreflightReport:
    profile: TargetProfile
    metrics: tuple[PathMetrics, ...]
    issues: tuple[PathIssue, ...]

    @property
    def errors(self) -> tuple[PathIssue, ...]:
        return tuple(issue for issue in self.issues if issue.severity == "error")

    @property
    def warnings(self) -> tuple[PathIssue, ...]:
        return tuple(issue for issue in self.issues if issue.severity == "warning")

    def raise_for_errors(self) -> None:
        if self.errors:
            raise PathPreflightError(self)


class PathPreflightError(ValueError):
    def __init__(self, report: PreflightReport):
        self.report = report
        details = "; ".join(issue.message for issue in report.errors[:3])
        super().__init__(f"Preflight percorsi non superato: {details}")


def _is_onedrive_root(segment: str) -> bool:
    normalized = segment.casefold()
    return normalized == "onedrive" or normalized.startswith("onedrive - ")


def detect_profile(root: str | os.PathLike[str]) -> TargetProfile:
    parts = PureWindowsPath(str(root)).parts
    if any(_is_onedrive_root(part) for part in parts):
        return ONEDRIVE
    if os.name == "nt" or re.match(r"^[A-Za-z]:[\\/]", str(root)):
        return WINDOWS_DESKTOP
    return MODERN_FILESYSTEM


def _segments(path: str) -> tuple[str, ...]:
    parsed = PureWindowsPath(path)
    return tuple(
        part for part in parsed.parts
        if part not in {parsed.anchor, "\\", "/"}
    )


def _onedrive_relative(path: str) -> str | None:
    parts = PureWindowsPath(path).parts
    for index, part in enumerate(parts):
        if _is_onedrive_root(part):
            remaining = parts[index + 1 :]
            return str(PureWindowsPath(*remaining)) if remaining else ""
    return None


def measure_path(path: str | os.PathLike[str]) -> PathMetrics:
    absolute = os.path.abspath(os.fspath(path))
    relative = _onedrive_relative(absolute)
    encoded = quote(relative.replace("\\", "/"), safe="/") if relative is not None else None
    segments = _segments(absolute)
    return PathMetrics(
        path=absolute,
        absolute_local=len(absolute),
        cloud_relative=len(relative) if relative is not None else None,
        encoded_risk=len(encoded) if encoded is not None else None,
        max_segment=max((len(part) for part in segments), default=0),
    )


def validate_segment(segment: str, path: str) -> list[PathIssue]:
    issues: list[PathIssue] = []
    stem = segment.split(".", 1)[0].upper()
    if any(char in INVALID_WINDOWS_CHARS for char in segment):
        issues.append(PathIssue("error", "invalid_character", path, segment, "Windows/OneDrive", f"Carattere non valido nel segmento '{segment}'"))
    if segment.endswith((" ", ".")):
        issues.append(PathIssue("error", "trailing_character", path, segment, "Windows/OneDrive", f"Spazio o punto terminale nel segmento '{segment}'"))
    if stem in RESERVED_WINDOWS_NAMES:
        issues.append(PathIssue("error", "reserved_name", path, segment, "Windows", f"Nome riservato Windows: '{segment}'"))
    return issues


def evaluate_paths(paths: list[str], profile: TargetProfile) -> PreflightReport:
    metrics = tuple(measure_path(path) for path in paths)
    issues: list[PathIssue] = []
    seen_segments: set[tuple[str, str]] = set()
    for item in metrics:
        for segment in _segments(item.path):
            key = (item.path, segment)
            if key not in seen_segments:
                issues.extend(validate_segment(segment, item.path))
                seen_segments.add(key)
            if len(segment) > profile.max_segment:
                issues.append(PathIssue("error", "segment_too_long", item.path, len(segment), profile.max_segment, f"Segmento di {len(segment)} caratteri oltre il limite {profile.max_segment}: '{segment}'"))
        checks = (
            ("absolute_local", item.absolute_local, profile.max_absolute),
            ("cloud_relative", item.cloud_relative, profile.max_cloud_relative),
            ("onedrive_sync", item.absolute_local, profile.max_onedrive_sync),
        )
        for code, value, limit in checks:
            if value is None or limit is None:
                continue
            if value > limit:
                severity = "warning" if profile is WINDOWS_DESKTOP and code == "absolute_local" else "error"
                issues.append(PathIssue(severity, code, item.path, value, limit, f"{code}: {value} caratteri oltre la soglia {limit}"))
            elif value >= int(limit * profile.warning_ratio):
                issues.append(PathIssue("warning", f"{code}_guard", item.path, value, limit, f"{code}: {value}/{limit} caratteri, nella fascia di guardia"))
        if item.encoded_risk is not None and profile.max_cloud_relative is not None and item.encoded_risk >= int(profile.max_cloud_relative * profile.warning_ratio):
            issues.append(PathIssue("warning", "encoded_risk", item.path, item.encoded_risk, profile.max_cloud_relative, f"Indicatore codificato prudenziale: {item.encoded_risk} (non è un conteggio hard OneDrive)"))
    return PreflightReport(profile, metrics, tuple(issues))


def expected_artifacts(
    output_root: str,
    record_name: str,
    record_type: str,
    formats: list[str] | tuple[str, ...],
    *,
    container_id: str | None = None,
    max_canvas: int | None = None,
) -> list[str]:
    """Enumera gli artefatti più lunghi e rappresentativi prodotti dal flusso D/R."""
    clean = re.sub(r'[\\/*?:"<>|]', "", record_name).replace(" ", "_").strip("_") or "documento"
    container = container_id or "CONTAINER_ID"
    work = os.path.join(output_root, f"{container}_{clean}")
    artifacts = [
        work,
        os.path.join(work, f"manifest_{container}_{clean}.json"),
        os.path.join(work, record_name, f"manifest_{container}_{clean}_genealogico.json"),
        os.path.join(work, record_name, f"manifest_{container}_{clean}_tecnico.json"),
    ]
    normalized = {str(value).upper().lstrip(".") for value in formats}
    extensions = [ext for ext in ("png", "jpg", "tif") if ext.upper() in normalized or (ext == "jpg" and "JPEG" in normalized) or (ext == "tif" and "TIFF" in normalized)]
    if "PDF" in normalized:
        artifacts.append(os.path.join(work, f"{clean}.pdf"))
    if record_type.upper() == "R":
        canvas = max(1, int(max_canvas or 9999))
        base = f"{record_name}_canvas_{canvas}"
        artifacts.extend([
            os.path.join(work, f"tiles_canvas_{canvas}"),
            os.path.join(work, f"{base}.json"),
            os.path.join(work, "_tmp_pdf_images", f"{base}_pdftmp.png"),
        ])
        artifacts.extend(os.path.join(work, f"{base}.{ext}") for ext in extensions)
    else:
        artifacts.extend(os.path.join(work, f"{record_name}.{ext}") for ext in extensions)
        artifacts.append(os.path.join(work, "tiles_doc"))
    return artifacts


def preflight_record(
    output_root: str,
    record_name: str,
    record_type: str,
    formats: list[str] | tuple[str, ...],
    *,
    container_id: str | None = None,
    max_canvas: int | None = None,
    profile: TargetProfile | None = None,
) -> PreflightReport:
    selected = profile or detect_profile(output_root)
    report = evaluate_paths(
        expected_artifacts(output_root, record_name, record_type, formats, container_id=container_id, max_canvas=max_canvas),
        selected,
    )
    raw_name_issues = tuple(validate_segment(record_name, record_name))
    if raw_name_issues:
        report = PreflightReport(report.profile, report.metrics, raw_name_issues + report.issues)
    return report
