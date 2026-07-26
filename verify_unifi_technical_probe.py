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
DEFAULT_REPORT = ROOT / ".codex_tmp" / "unifi_technical_probe.csv"
DEFAULT_USER_AGENT = "ATK-Pro UniFI technical probe (user-run local verification)"
UUID_RE = r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}"


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
ITEM_RE = re.compile(rf"/items/(?P<uuid>{UUID_RE})\b", re.IGNORECASE)
ENTITY_RE = re.compile(rf"/entities/(?P<entity_type>[a-z-]+)/(?P<uuid>{UUID_RE})\b", re.IGNORECASE)
REST_ITEM_RE = re.compile(rf"/server/api/core/items/(?P<uuid>{UUID_RE})\b", re.IGNORECASE)
REST_ITEM_SUBRESOURCE_RE = re.compile(
    rf"/server/api/core/items/(?P<uuid>{UUID_RE})/(?P<subresource>[a-zA-Z][a-zA-Z0-9_-]*)\b",
    re.IGNORECASE,
)
REST_BUNDLE_RE = re.compile(
    rf"/server/api/core/bundles/(?P<uuid>{UUID_RE})(?:/(?P<subresource>[a-zA-Z][a-zA-Z0-9_-]*))?\b",
    re.IGNORECASE,
)
REST_BITSTREAM_RE = re.compile(
    rf"/server/api/core/bitstreams/(?P<uuid>{UUID_RE})(?:/(?P<subresource>[a-zA-Z][a-zA-Z0-9_-]*))?\b",
    re.IGNORECASE,
)


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


def _is_unifi_host(netloc: str) -> bool:
    return netloc.lower() == "improntedigitali.unifi.it"


def _classify_url(url: str) -> tuple[str, str, str] | None:
    parsed = urlparse(url)
    netloc = parsed.netloc.lower()
    path = parsed.path
    path_lower = path.lower()

    if not _is_unifi_host(netloc):
        return None

    item_subresource_match = REST_ITEM_SUBRESOURCE_RE.search(path)
    if item_subresource_match:
        subresource = item_subresource_match.group("subresource").lower()
        return "api_item", f"unifi_item_{subresource}", item_subresource_match.group("uuid")

    item_match = REST_ITEM_RE.search(path)
    if item_match:
        return "api_item", "unifi_rest_item", item_match.group("uuid")

    item_match = ITEM_RE.search(path)
    if item_match:
        return "catalog_record", "unifi_item", item_match.group("uuid")

    entity_match = ENTITY_RE.search(path)
    if entity_match:
        return "entity", f"unifi_{entity_match.group('entity_type')}", entity_match.group("uuid")

    bundle_match = REST_BUNDLE_RE.search(path)
    if bundle_match:
        subresource = bundle_match.group("subresource")
        if subresource:
            return "bundle", f"unifi_bundle_{subresource.lower()}", bundle_match.group("uuid")
        return "bundle", "unifi_bundle_metadata", bundle_match.group("uuid")

    bitstream_match = REST_BITSTREAM_RE.search(path)
    if bitstream_match:
        subresource = bitstream_match.group("subresource")
        if subresource and subresource.lower() == "content":
            return "bitstream", "unifi_bitstream_content", bitstream_match.group("uuid")
        if subresource:
            return "bitstream", f"unifi_bitstream_{subresource.lower()}", bitstream_match.group("uuid")
        return "bitstream", "unifi_bitstream_metadata", bitstream_match.group("uuid")

    if "/server/api/core/bitstreamformats/" in path_lower:
        return "format", "unifi_bitstream_format", path.rsplit("/", 1)[-1]

    if path_lower.endswith((".jpg", ".jpeg", ".png", ".webp", ".tif", ".tiff", ".svg")):
        if "/assets/images/mirador-logo" in path_lower:
            return "viewer_asset", "mirador_brand_asset", path.rsplit("/", 1)[-1]
        if any(token in path_lower for token in ("/assets/", "/themes/", "/logo", "/icons/", "favicon")):
            return "image", "site_asset", ""
        return "image", "public_image", path.rsplit("/", 1)[-1]

    return None


def extract_candidates(html: str, base_url: str) -> list[ProbeCandidate]:
    seen: set[tuple[str, str]] = set()
    candidates: list[ProbeCandidate] = []

    raw_urls: list[tuple[str, str]] = [(base_url, "input_url")]
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
        return "Nessun item UniFI/DSpace-GLAM, bundle, bitstream, thumbnail o immagine candidata trovato."
    counts: dict[str, int] = {}
    roles: dict[str, int] = {}
    for candidate in candidates:
        counts[candidate.kind] = counts.get(candidate.kind, 0) + 1
        roles[candidate.role] = roles.get(candidate.role, 0) + 1
    kind_summary = ", ".join(f"{kind}: {count}" for kind, count in sorted(counts.items()))
    role_summary = ", ".join(f"{role}: {count}" for role, count in sorted(roles.items()))
    return f"{kind_summary} | {role_summary}"


def _evaluate_readiness(candidates: list[ProbeCandidate]) -> str:
    roles = {candidate.role for candidate in candidates}
    has_public_item = "unifi_item" in roles or "unifi_rest_item" in roles
    has_bundle_or_bitstream = any(role.startswith("unifi_bundle_") or role.startswith("unifi_bitstream_") for role in roles)
    has_thumbnail = "unifi_item_thumbnail" in roles or "unifi_bitstream_thumbnail" in roles or "public_image" in roles

    if has_public_item and has_bundle_or_bitstream and has_thumbnail:
        return "GO/NO-GO: REVIEW (record, API e surrogate pubblici emersi; verificare se esiste un percorso manifesto/download no-login)"
    if has_public_item and has_bundle_or_bitstream:
        return "GO/NO-GO: HOLD (backend pubblico emerso, ma i surrogate visivi o il percorso di consultazione restano incompleti)"
    if has_public_item:
        return "GO/NO-GO: HOLD (item pubblico emerso, ma non ancora un pattern tecnico sufficiente)"
    return "GO/NO-GO: NO_GO (nessun item o backend tecnico pubblico riusabile emerso)"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Sonda tecnica prudente per Impronte Digitali UniFI: cerca item "
            "pubblici, API DSpace-GLAM, bundle, bitstream, thumbnail e "
            "surrogate visivi senza dedurre automaticamente un download pubblico."
        )
    )
    parser.add_argument("--url", help="Pagina pubblica UniFI/DSpace-GLAM da sondare.")
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
        print(f"ERRORE: impossibile leggere la pagina UniFI: {exc}", file=sys.stderr)
        return 2

    candidates = extract_candidates(html, base_url)
    write_report(args.output, candidates)

    print(f"Pagina: {base_url}")
    print(f"Candidati trovati: {len(candidates)}")
    print(f"Report: {args.output}")
    print(_summarize(candidates))
    print(_evaluate_readiness(candidates))
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
