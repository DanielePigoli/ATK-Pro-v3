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
DEFAULT_REPORT = ROOT / ".codex_tmp" / "phaidra_technical_probe.csv"
DEFAULT_USER_AGENT = "ATK-Pro PHAIDRA technical probe (user-run local verification)"


@dataclass(frozen=True)
class ProbeCandidate:
    kind: str
    role: str
    identifier: str
    url: str
    source: str


ATTR_URL_RE = re.compile(
    r"""(?ix)
    \b(?:href|src|poster|data-(?:href|src|url|manifest|iiif|json)|content)\s*=\s*
    (?P<quote>["'])
    (?P<url>[^"']+)
    (?P=quote)
    """
)
ABSOLUTE_URL_RE = re.compile(r"https?://[^\s\"'<>\\)]+", re.IGNORECASE)
OBJECT_RE = re.compile(r"/(?:view|detail|api/object)/(?P<object_id>o:[0-9]+)(?:[/?#]|$)", re.IGNORECASE)
RIGHTS_NOTICE_RE = re.compile(
    r"(?i)\b(all rights reserved|tutti i diritti riservati)\b"
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
    if not value.startswith(("http://", "https://", "/")):
        return None
    return urljoin(base_url, value)


def _identifier_from_path(path: str) -> str:
    parts = [part for part in path.strip("/").split("/") if part]
    if not parts:
        return ""
    return parts[-1]


def _classify_url(url: str) -> tuple[str, str, str] | None:
    parsed = urlparse(url)
    netloc = parsed.netloc.lower()
    path = parsed.path
    path_lower = path.lower()
    query_lower = parsed.query.lower()

    if "phaidra" not in netloc:
        return None

    object_match = OBJECT_RE.search(path)
    object_id = object_match.group("object_id") if object_match else ""

    if "/api/object/" in path_lower and path_lower.endswith("/iiifmanifest"):
        return "manifest", "phaidra_iiif_manifest", object_id or _identifier_from_path(path)

    if "/api/imageserver" in path_lower and "iiif=" in query_lower and path_lower.endswith("imageserver"):
        if query_lower.endswith("/info.json"):
            return "iiif_info", "phaidra_info_json", object_id
        return "image", "iiif_content_image", object_id

    if "/api/object/" in path_lower and path_lower.endswith("/download"):
        return "pdf", "phaidra_download", object_id or _identifier_from_path(path)

    if "/detail/" in path_lower and path_lower.endswith(".download"):
        detail_id = path.split("/")[-1].removesuffix(".download")
        return "pdf", "phaidra_download", detail_id

    if "/api/object/" in path_lower and path_lower.endswith("/thumbnail"):
        return "image", "phaidra_thumbnail", object_id or _identifier_from_path(path)

    if "/api/object/" in path_lower and any(
        path_lower.endswith(suffix)
        for suffix in ("/index/dc", "/datacite", "/lom", "/edm", "/openaire", "/uwmetadata")
    ):
        return "metadata_export", "phaidra_metadata_export", object_id or _identifier_from_path(path)

    if any(token in path_lower for token in ("/view/", "/detail/")) and object_id:
        return "catalog_record", "phaidra_object_page", object_id

    if path_lower.endswith((".jpg", ".jpeg", ".png", ".webp", ".tif", ".tiff")):
        return "image", "candidate", _identifier_from_path(path)

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

    rights_match = RIGHTS_NOTICE_RE.search(html)
    if rights_match:
        base_identifier = ""
        try:
            parsed_base = urlparse(base_url)
            object_match = OBJECT_RE.search(parsed_base.path)
            if object_match:
                base_identifier = object_match.group("object_id")
        except Exception:
            base_identifier = ""
        candidates.append(
            ProbeCandidate(
                kind="rights_notice",
                role="phaidra_rights_notice",
                identifier=base_identifier,
                url=base_url,
                source=rights_match.group(1),
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
        return "Nessun record PHAIDRA, manifest, info.json, immagine, PDF, export metadati o notice diritti candidato trovato."
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
    restrictive_rights = any(
        candidate.role == "phaidra_rights_notice"
        and candidate.source.lower() in {"all rights reserved", "tutti i diritti riservati"}
        for candidate in candidates
    )

    if "phaidra_iiif_manifest" not in roles:
        return "GO/NO-GO: NO_GO (nessun manifest IIIF pubblico stabile emerso)"
    if restrictive_rights:
        return "GO/NO-GO: HOLD (manifest pubblico presente ma rights item-level restrittivi)"
    if "phaidra_download" in roles:
        return "GO/NO-GO: REVIEW (manifest e download pubblico emersi; verificare coerenza con licenza item-level)"
    return "GO/NO-GO: REVIEW (manifest pubblico emerso; verificare licenza o rights notice del singolo oggetto)"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Sonda tecnica prudente per PHAIDRA: cerca pagina oggetto, "
            "IIIF manifest, endpoint immagini IIIF, download e export metadati."
        )
    )
    parser.add_argument("--url", help="Pagina pubblica PHAIDRA da sondare.")
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
        print(f"ERRORE: impossibile leggere la pagina PHAIDRA: {exc}", file=sys.stderr)
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
