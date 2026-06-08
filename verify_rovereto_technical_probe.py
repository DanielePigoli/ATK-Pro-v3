from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urljoin, urlparse
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parent
DEFAULT_REPORT = ROOT / ".codex_tmp" / "rovereto_technical_probe.csv"
DEFAULT_BITSTREAM_REPORT = ROOT / ".codex_tmp" / "rovereto_bitstream_summary.csv"
DEFAULT_USER_AGENT = "ATK-Pro Rovereto technical probe (user-run local verification)"


@dataclass(frozen=True)
class ProbeCandidate:
    kind: str
    role: str
    identifier: str
    url: str
    source: str


@dataclass(frozen=True)
class BitstreamSummary:
    identifier: str
    name: str
    sequence_id: str
    size_bytes: str
    checksum: str
    checksum_algorithm: str
    format_label: str
    format_mimetype: str
    metadata_url: str
    content_url: str
    bundle_url: str
    thumbnail_url: str


ATTR_URL_RE = re.compile(
    r"""(?ix)
    \b(?:href|src|data-[a-z0-9_-]+|content)\s*=\s*
    (?P<quote>["'])
    (?P<url>[^"']+)
    (?P=quote)
    """
)
ABSOLUTE_URL_RE = re.compile(r"https?://[^\s\"'<>\\)]+", re.IGNORECASE)
JSON_URL_RE = re.compile(
    r"""(?ix)
    "(?:href|self|url)"\s*:\s*
    (?P<quote>["'])
    (?P<url>[^"']+)
    (?P=quote)
    """
)
UUID_RE = r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}"
ENTITY_RE = re.compile(rf"/entities/(?P<entity_type>[a-z-]+)/(?P<uuid>{UUID_RE})\b", re.IGNORECASE)
HANDLE_RE = re.compile(r"/handle/(?P<prefix>\d+(?:\.\d+)+)/(?P<handle_id>\d+)\b", re.IGNORECASE)
REST_ITEM_RE = re.compile(rf"/server/api/core/items/(?P<uuid>{UUID_RE})\b", re.IGNORECASE)
REST_ITEM_SUBRESOURCE_RE = re.compile(
    rf"/server/api/core/items/(?P<uuid>{UUID_RE})/(?P<subresource>[a-zA-Z][a-zA-Z0-9_-]*)\b",
    re.IGNORECASE,
)
REST_BUNDLE_RE = re.compile(rf"/server/api/core/bundles/(?P<uuid>{UUID_RE})(?:/(?P<subresource>[a-zA-Z][a-zA-Z0-9_-]*))?\b", re.IGNORECASE)
REST_BITSTREAM_RE = re.compile(
    rf"/server/api/core/bitstreams/(?P<uuid>{UUID_RE})(?:/(?P<subresource>[a-zA-Z][a-zA-Z0-9_-]*))?\b",
    re.IGNORECASE,
)


def _load_url(url: str, timeout: int) -> str:
    request = Request(
        url,
        headers={
            "User-Agent": DEFAULT_USER_AGENT,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,application/json;q=0.8,application/pdf;q=0.7,*/*;q=0.6",
            "Accept-Language": "it-IT,it;q=0.9,en;q=0.7",
        },
    )
    with urlopen(request, timeout=timeout) as response:
        raw = response.read()
        content_type = response.headers.get_content_type()
        encoding = response.headers.get_content_charset() or "utf-8"
    if content_type == "application/pdf":
        return f'<a href="{url}">PDF diretto Rovereto</a>'
    return raw.decode(encoding, errors="replace")


def _load_json_url(url: str, timeout: int) -> dict:
    text = _load_url(url, timeout)
    data = json.loads(text)
    if not isinstance(data, dict):
        raise ValueError("risposta JSON non oggetto")
    return data


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
    is_rovereto = "digitallibrary.bibliotecacivica.rovereto.tn.it" in netloc

    if is_rovereto:
        entity_match = ENTITY_RE.search(path)
        if entity_match:
            return "entity", f"dspace_{entity_match.group('entity_type')}", entity_match.group("uuid")

        handle_match = HANDLE_RE.search(path)
        if handle_match:
            return "handle", "persistent_handle", f"{handle_match.group('prefix')}/{handle_match.group('handle_id')}"

        item_subresource_match = REST_ITEM_SUBRESOURCE_RE.search(path)
        if item_subresource_match:
            subresource = item_subresource_match.group("subresource").lower()
            return "api_item", f"dspace_item_{subresource}", item_subresource_match.group("uuid")

        bundle_match = REST_BUNDLE_RE.search(path)
        if bundle_match:
            subresource = bundle_match.group("subresource")
            if subresource:
                return "bundle", f"bundle_{subresource.lower()}", bundle_match.group("uuid")
            return "bundle", "bundle_metadata", bundle_match.group("uuid")

        bitstream_match = REST_BITSTREAM_RE.search(path)
        if bitstream_match:
            subresource = bitstream_match.group("subresource")
            if subresource and subresource.lower() == "content":
                return "bitstream", "bitstream_content", bitstream_match.group("uuid")
            if subresource:
                return "bitstream", f"bitstream_{subresource.lower()}", bitstream_match.group("uuid")
            return "bitstream", "bitstream_metadata", bitstream_match.group("uuid")

        item_match = REST_ITEM_RE.search(path)
        if item_match:
            return "api_item", "dspace_rest_item", item_match.group("uuid")

        if path_lower.endswith(".pdf"):
            return "pdf", "document_pdf", ""
        if path_lower.endswith((".jpg", ".jpeg", ".png", ".webp", ".tif", ".tiff")):
            if any(token in path_lower for token in ("/assets/", "/themes/", "/logo", "/icons/", "favicon")):
                return "image", "site_asset", ""
            return "image", "candidate", ""

    if "mirador" in path_lower or "mirador" in query_lower:
        return "viewer", "mirador_viewer", ""
    if path_lower.endswith(("manifest", "manifest.json")) or "manifest=" in query_lower or "manifestid=" in query_lower:
        return "manifest", "candidate", ""
    if path_lower.endswith("info.json") or "/info.json" in path_lower:
        return "iiif_info", "candidate", ""
    if "/iiif/" in path_lower:
        return "iiif_related", "candidate", ""
    return None


def _derive_rovereto_api_item(url: str) -> str | None:
    parsed = urlparse(url)
    if "digitallibrary.bibliotecacivica.rovereto.tn.it" not in parsed.netloc.lower():
        return None
    entity_match = ENTITY_RE.search(parsed.path)
    if not entity_match:
        return None
    return f"{parsed.scheme}://{parsed.netloc}/server/api/core/items/{entity_match.group('uuid')}"


def extract_candidates(html: str, base_url: str) -> list[ProbeCandidate]:
    seen: set[tuple[str, str]] = set()
    candidates: list[ProbeCandidate] = []

    raw_urls: list[tuple[str, str]] = []
    raw_urls.append((base_url, "input_url"))
    raw_urls.extend((m.group("url"), "html_attribute") for m in ATTR_URL_RE.finditer(html))
    raw_urls.extend((m.group("url"), "json_link") for m in JSON_URL_RE.finditer(html))
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
        api_item_url = _derive_rovereto_api_item(normalized)
        if api_item_url and ("api_item", api_item_url) not in seen:
            api_classification = _classify_url(api_item_url)
            if api_classification:
                api_kind, api_role, api_identifier = api_classification
                seen.add((api_kind, api_item_url))
                candidates.append(
                    ProbeCandidate(
                        kind=api_kind,
                        role=api_role,
                        identifier=api_identifier,
                        url=api_item_url,
                        source="derived_from_entity",
                    )
                )

    return sorted(candidates, key=lambda c: (c.kind, c.role, c.identifier, c.url))


def _should_follow_candidate(candidate: ProbeCandidate) -> bool:
    if candidate.kind not in {"api_item", "bundle", "bitstream"}:
        return False
    if candidate.role.endswith("_content"):
        return False
    return "digitallibrary.bibliotecacivica.rovereto.tn.it/server/api/" in candidate.url.lower()


def collect_candidates(
    html: str,
    base_url: str,
    *,
    follow_json: bool = False,
    timeout: int = 25,
    max_depth: int = 2,
) -> list[ProbeCandidate]:
    candidates = extract_candidates(html, base_url)
    if not follow_json or max_depth <= 0:
        return candidates

    by_key: dict[tuple[str, str], ProbeCandidate] = {(candidate.kind, candidate.url): candidate for candidate in candidates}
    visited: set[str] = set()
    frontier = [candidate for candidate in candidates if _should_follow_candidate(candidate)]

    for _depth in range(max_depth):
        next_frontier: list[ProbeCandidate] = []
        for candidate in frontier:
            if candidate.url in visited:
                continue
            visited.add(candidate.url)
            try:
                linked_html = _load_url(candidate.url, timeout)
            except Exception as exc:
                print(f"AVVISO: impossibile seguire {candidate.url}: {exc}", file=sys.stderr)
                continue
            for linked_candidate in extract_candidates(linked_html, candidate.url):
                key = (linked_candidate.kind, linked_candidate.url)
                if key in by_key:
                    continue
                by_key[key] = linked_candidate
                if _should_follow_candidate(linked_candidate):
                    next_frontier.append(linked_candidate)
        if not next_frontier:
            break
        frontier = next_frontier

    return sorted(by_key.values(), key=lambda c: (c.kind, c.role, c.identifier, c.url))


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


def _json_link(data: dict, name: str) -> str:
    links = data.get("_links")
    if not isinstance(links, dict):
        return ""
    entry = links.get(name)
    if not isinstance(entry, dict):
        return ""
    href = entry.get("href")
    return href if isinstance(href, str) else ""


def _extract_format_info(data: dict, timeout: int) -> tuple[str, str]:
    embedded_format = data.get("format")
    if isinstance(embedded_format, dict):
        label = embedded_format.get("shortDescription") or embedded_format.get("description") or embedded_format.get("mimetype")
        mimetype = embedded_format.get("mimetype")
        return str(label or ""), str(mimetype or "")

    format_url = _json_link(data, "format")
    if not format_url:
        return "", ""
    try:
        format_data = _load_json_url(format_url, timeout)
    except Exception as exc:
        print(f"AVVISO: impossibile leggere formato bitstream {format_url}: {exc}", file=sys.stderr)
        return "", ""
    label = format_data.get("shortDescription") or format_data.get("description") or format_data.get("mimetype")
    mimetype = format_data.get("mimetype")
    return str(label or ""), str(mimetype or "")


def summarize_bitstreams(candidates: list[ProbeCandidate], timeout: int = 25) -> list[BitstreamSummary]:
    summaries: list[BitstreamSummary] = []
    seen: set[str] = set()
    metadata_candidates = [
        candidate
        for candidate in candidates
        if candidate.kind == "bitstream" and candidate.role == "bitstream_metadata"
    ]

    for candidate in sorted(metadata_candidates, key=lambda item: (item.identifier, item.url)):
        if candidate.identifier in seen:
            continue
        seen.add(candidate.identifier)
        try:
            data = _load_json_url(candidate.url, timeout)
        except Exception as exc:
            print(f"AVVISO: impossibile leggere metadati bitstream {candidate.url}: {exc}", file=sys.stderr)
            continue
        checksum = data.get("checkSum") if isinstance(data.get("checkSum"), dict) else {}
        format_label, format_mimetype = _extract_format_info(data, timeout)
        summaries.append(
            BitstreamSummary(
                identifier=str(data.get("uuid") or candidate.identifier),
                name=str(data.get("name") or ""),
                sequence_id=str(data.get("sequenceId") or ""),
                size_bytes=str(data.get("sizeBytes") or ""),
                checksum=str(checksum.get("value") or ""),
                checksum_algorithm=str(checksum.get("algorithm") or ""),
                format_label=format_label,
                format_mimetype=format_mimetype,
                metadata_url=candidate.url,
                content_url=_json_link(data, "content"),
                bundle_url=_json_link(data, "bundle"),
                thumbnail_url=_json_link(data, "thumbnail"),
            )
        )

    return sorted(summaries, key=lambda item: (_natural_sort_key(item.name), item.sequence_id, item.identifier))


def _natural_sort_key(value: str) -> list[tuple[int, int | str]]:
    parts: list[tuple[int, int | str]] = []
    for part in re.split(r"(\d+)", value.lower()):
        if part.isdigit():
            parts.append((0, int(part)))
        elif part:
            parts.append((1, part))
    return parts


def write_bitstream_report(path: Path, summaries: list[BitstreamSummary]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(
            fh,
            fieldnames=[
                "identifier",
                "name",
                "sequence_id",
                "size_bytes",
                "format_label",
                "format_mimetype",
                "checksum_algorithm",
                "checksum",
                "metadata_url",
                "content_url",
                "bundle_url",
                "thumbnail_url",
            ],
        )
        writer.writeheader()
        for item in summaries:
            writer.writerow(
                {
                    "identifier": item.identifier,
                    "name": item.name,
                    "sequence_id": item.sequence_id,
                    "size_bytes": item.size_bytes,
                    "format_label": item.format_label,
                    "format_mimetype": item.format_mimetype,
                    "checksum_algorithm": item.checksum_algorithm,
                    "checksum": item.checksum,
                    "metadata_url": item.metadata_url,
                    "content_url": item.content_url,
                    "bundle_url": item.bundle_url,
                    "thumbnail_url": item.thumbnail_url,
                }
            )


def _summarize(candidates: list[ProbeCandidate]) -> str:
    if not candidates:
        return "Nessun candidato Rovereto/DSpace-GLAM, manifest, info.json, file o viewer trovato."
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
            "Sonda tecnica prudente per Rovereto Digital Library / DSpace-GLAM: "
            "cerca entity, handle, API item/bitstream, manifest, info.json, file e viewer."
        )
    )
    parser.add_argument("--url", help="Pagina pubblica Rovereto/DSpace-GLAM da sondare.")
    parser.add_argument("--html-fixture", type=Path, help="Fixture HTML locale per test offline.")
    parser.add_argument("--output", type=Path, default=DEFAULT_REPORT, help="Report CSV da creare.")
    parser.add_argument(
        "--bitstream-output",
        type=Path,
        default=DEFAULT_BITSTREAM_REPORT,
        help="Report CSV qualitativo dei bitstream da creare con --summarize-bitstreams.",
    )
    parser.add_argument("--timeout", type=int, default=25, help="Timeout rete in secondi.")
    parser.add_argument(
        "--follow-json",
        action="store_true",
        help="Segue in modo limitato i link API/HAL DSpace trovati, senza aprire contenuti binari.",
    )
    parser.add_argument("--max-depth", type=int, default=2, help="Profondita massima per --follow-json.")
    parser.add_argument(
        "--summarize-bitstreams",
        action="store_true",
        help="Legge solo metadati/formato dei bitstream trovati e crea un CSV qualitativo, senza aprire /content.",
    )
    args = parser.parse_args(argv)

    if not args.url and not args.html_fixture:
        parser.error("specificare --url oppure --html-fixture")
    if args.html_fixture and not args.url:
        parser.error("con --html-fixture serve anche --url come base per gli URL relativi")

    base_url = args.url
    try:
        html = _load_fixture(args.html_fixture) if args.html_fixture else _load_url(args.url, args.timeout)
    except Exception as exc:
        print(f"ERRORE: impossibile leggere la pagina Rovereto: {exc}", file=sys.stderr)
        return 2

    candidates = collect_candidates(
        html,
        base_url,
        follow_json=args.follow_json,
        timeout=args.timeout,
        max_depth=args.max_depth,
    )
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
    if args.summarize_bitstreams:
        summaries = summarize_bitstreams(candidates, timeout=args.timeout)
        write_bitstream_report(args.bitstream_output, summaries)
        print(f"Report bitstream: {args.bitstream_output}")
        print(f"Bitstream sintetizzati: {len(summaries)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
