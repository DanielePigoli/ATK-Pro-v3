from __future__ import annotations

import argparse
import csv
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urljoin, urlparse
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parent
DEFAULT_REPORT = ROOT / ".codex_tmp" / "ambrosiana_technical_probe.csv"
DEFAULT_USER_AGENT = "ATK-Pro Ambrosiana technical probe (user-run local verification)"


@dataclass(frozen=True)
class ProbeCandidate:
    kind: str
    role: str
    identifier: str
    url: str
    source: str


ATTR_URL_RE = re.compile(
    r"""(?ix)
    \b(?:href|src|data-[a-z0-9_-]+|content)\s*=\s*
    (?P<quote>["'])
    (?P<url>[^"']+)
    (?P=quote)
    """
)
ABSOLUTE_URL_RE = re.compile(r"https?://[^\s\"'<>\\)]+", re.IGNORECASE)
AMBRO_CATALOG_RE = re.compile(r"/opac/detail/view/ambro:catalog:(?P<catalog_id>\d+)", re.IGNORECASE)
DIAMM_MANIFEST_RE = re.compile(r"/manifests/(?P<identifier>[^/]+)/manifest\.json$", re.IGNORECASE)


def _load_url(url: str, timeout: int) -> str:
    request = Request(
        url,
        headers={
            "User-Agent": DEFAULT_USER_AGENT,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,application/json;q=0.8,*/*;q=0.7",
            "Accept-Language": "it-IT,it;q=0.9,en;q=0.7",
        },
    )
    with urlopen(request, timeout=timeout) as response:
        raw = response.read()
        encoding = response.headers.get_content_charset() or "utf-8"
    return raw.decode(encoding, errors="replace")


def _load_fixture(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _clean_url(raw: str, base_url: str) -> str | None:
    value = raw.strip().replace("&amp;", "&").rstrip(".,;")
    if not value or value.startswith(("#", "javascript:", "mailto:", "tel:")):
        return None
    return urljoin(base_url, value)


def _classify_url(url: str) -> tuple[str, str, str] | None:
    parsed = urlparse(url)
    netloc = parsed.netloc.lower()
    path = parsed.path
    path_lower = path.lower()
    query_lower = parsed.query.lower()

    catalog_match = AMBRO_CATALOG_RE.search(path)
    if "ambrosiana.comperio.it" in netloc and catalog_match:
        return "catalog_record", "comperio_record", catalog_match.group("catalog_id")

    if "/mirador" in path_lower or "mirador" in query_lower:
        return "viewer", "mirador_viewer", ""

    diamm_match = DIAMM_MANIFEST_RE.search(path)
    if "iiif.diamm.net" in netloc and diamm_match:
        return "manifest", "external_diamm_manifest", diamm_match.group("identifier")

    if path_lower.endswith(("manifest", "manifest.json")) or "manifest=" in query_lower or "manifestid=" in query_lower:
        return "manifest", "candidate", ""
    if path_lower.endswith("info.json") or "/info.json" in path_lower:
        return "iiif_info", "candidate", ""
    if "/cantaloupe/" in path_lower and path_lower.endswith((".jpg", ".jpeg", ".png", ".webp", ".tif", ".tiff")):
        return "image", "cantaloupe_image", ""
    if path_lower.endswith((".jpg", ".jpeg", ".png", ".webp", ".tif", ".tiff")):
        if any(token in path_lower for token in ("/assets/", "/themes/", "/logo", "/icons/", "favicon")):
            return "image", "site_asset", ""
        return "image", "candidate", ""
    return None


def extract_candidates(html: str, base_url: str) -> list[ProbeCandidate]:
    seen: set[tuple[str, str]] = set()
    candidates: list[ProbeCandidate] = []

    raw_urls: list[tuple[str, str]] = []
    raw_urls.extend((m.group("url"), "html_attribute") for m in ATTR_URL_RE.finditer(html))
    raw_urls.extend((m.group(0), "absolute_text") for m in ABSOLUTE_URL_RE.finditer(html))

    for raw, source in raw_urls:
        normalized = _clean_url(raw, base_url)
        if not normalized:
            continue
        classification = _classify_url(normalized)
        if not classification:
            continue
        kind, role, identifier = classification
        key = (kind, normalized)
        if key in seen:
            continue
        seen.add(key)
        candidates.append(
            ProbeCandidate(
                kind=kind,
                role=role,
                identifier=identifier,
                url=normalized,
                source=source,
            )
        )

    return sorted(candidates, key=lambda c: (c.kind, c.role, c.identifier, c.url))


def write_report(path: Path, candidates: list[ProbeCandidate]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=["kind", "role", "identifier", "url", "source"])
        writer.writeheader()
        for candidate in candidates:
            writer.writerow(
                {
                    "kind": candidate.kind,
                    "role": candidate.role,
                    "identifier": candidate.identifier,
                    "url": candidate.url,
                    "source": candidate.source,
                }
            )


def _summarize(candidates: list[ProbeCandidate]) -> str:
    if not candidates:
        return "Nessun record Ambrosiana, manifest, info.json, immagine o viewer candidato trovato."
    counts: dict[str, int] = {}
    roles: dict[str, int] = {}
    for candidate in candidates:
        counts[candidate.kind] = counts.get(candidate.kind, 0) + 1
        roles[candidate.role] = roles.get(candidate.role, 0) + 1
    kind_summary = ", ".join(f"{kind}: {count}" for kind, count in sorted(counts.items()))
    role_summary = ", ".join(f"{role}: {count}" for role, count in sorted(roles.items()))
    return f"{kind_summary} | {role_summary}"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Sonda tecnica prudente per Ambrosiana Digitale: cerca record Comperio, "
            "manifest IIIF, info.json, immagini Cantaloupe/Mirador e viewer."
        )
    )
    parser.add_argument("--url", help="Pagina pubblica Ambrosiana/Comperio/IIIF da sondare.")
    parser.add_argument("--html-fixture", type=Path, help="Fixture HTML locale per test offline.")
    parser.add_argument("--output", type=Path, default=DEFAULT_REPORT, help="Report CSV da creare.")
    parser.add_argument("--timeout", type=int, default=25, help="Timeout rete in secondi.")
    args = parser.parse_args(argv)

    if not args.url and not args.html_fixture:
        parser.error("specificare --url oppure --html-fixture")
    if args.html_fixture and not args.url:
        parser.error("con --html-fixture serve anche --url come base per gli URL relativi")

    base_url = args.url
    try:
        html = _load_fixture(args.html_fixture) if args.html_fixture else _load_url(args.url, args.timeout)
    except Exception as exc:
        print(f"ERRORE: impossibile leggere la pagina Ambrosiana: {exc}", file=sys.stderr)
        return 2

    candidates = extract_candidates(html, base_url)
    write_report(args.output, candidates)

    print(f"Pagina: {base_url}")
    print(f"Candidati trovati: {len(candidates)}")
    print(f"Report: {args.output}")
    print(_summarize(candidates))
    for candidate in candidates[:20]:
        label = f"{candidate.kind} [{candidate.role}]"
        if candidate.identifier:
            label += f" {candidate.identifier}"
        print(f"- {label}: {candidate.url}")
    if len(candidates) > 20:
        print(f"... altri {len(candidates) - 20} candidati nel report CSV")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
