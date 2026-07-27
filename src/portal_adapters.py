from __future__ import annotations

from dataclasses import dataclass
from io import BytesIO
import re

import requests
from PIL import Image
try:
    from portal_registry import get_portal_referer, get_portal_tile_download_policy
except ImportError:  # pragma: no cover - package import path
    from src.portal_registry import get_portal_referer, get_portal_tile_download_policy


@dataclass(frozen=True)
class DirectImagePortalAdapter:
    portal_label: str
    referer: str
    timeout: int = 45
    host_fragment: str | None = None

    def download_image(self, image_url: str):
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Referer": self.referer,
        }
        response = requests.get(image_url, headers=headers, timeout=self.timeout)
        if not response.ok or not response.content:
            return None, response.status_code if response is not None else None, 0
        image = Image.open(BytesIO(response.content)).copy()
        return image, response.status_code, len(response.content)

    def matches_service_id(self, service_id: str | None) -> bool:
        return bool(self.host_fragment and service_id and self.host_fragment in service_id)

    def extract_image_from_canvas(self, canvas: dict, service_id: str | None = None) -> str | None:
        try:
            resource = canvas.get("images", [{}])[0].get("resource", {})
            service = resource.get("service") or {}
            if isinstance(service, list):
                service = service[0] if service else {}
            if isinstance(service, dict):
                image_url = service.get("@id") or service.get("id") or service_id
                return str(image_url).strip() if image_url else None
        except Exception:
            return None
        return None


@dataclass(frozen=True)
class DirectPdfPortalAdapter:
    portal_label: str
    referer: str
    default_name: str

    def extract_pdf_from_manifest(self, manifest):
        if not isinstance(manifest, dict):
            return None
        see_also_entries = manifest.get("seeAlso") or manifest.get("see_also") or []
        if isinstance(see_also_entries, dict):
            see_also_entries = [see_also_entries]
        for entry in see_also_entries:
            pdf_url = _extract_pdf_url_from_entry(entry)
            if pdf_url:
                return str(pdf_url)
        return None

    def extract_pdf_from_service(self, service):
        if not isinstance(service, dict):
            return None
        pdf_url = service.get("pdf_url") or _extract_pdf_url_from_entry(service)
        return str(pdf_url) if pdf_url else None


@dataclass(frozen=True)
class PortalRequestAdapter:
    portal_key: str | None
    referer: str | None
    tile_max_workers: int | None
    tile_inter_delay: float

    @classmethod
    def for_portal(cls, portal_key: str | None, source_url: str | None = None):
        tile_max_workers, tile_inter_delay = get_portal_tile_download_policy(portal_key)
        return cls(
            portal_key=portal_key,
            referer=get_portal_referer(portal_key, source_url),
            tile_max_workers=tile_max_workers,
            tile_inter_delay=tile_inter_delay,
        )


@dataclass(frozen=True)
class SyntheticManifestPortalAdapter:
    portal_key: str
    portal_label: str

    def build_manifest(self, page_url: str, scraped_html: str | None = None):
        if self.portal_key == "biblioteca_digitale_trentina":
            return _build_bdt_synthetic_manifest(page_url, scraped_html)
        if self.portal_key == "biblioteca_digitale_lombarda":
            return _build_bdl_pdf_manifest(page_url)
        if self.portal_key == "rovereto_digital_library":
            return _build_rovereto_synthetic_manifest(page_url)
        if self.portal_key == "doge_unige":
            return _build_doge_synthetic_manifest(page_url)
        if self.portal_key == "matricula":
            return _build_matricula_synthetic_manifest(page_url, scraped_html)
        if self.portal_key == "internet_archive":
            return _build_internet_archive_synthetic_manifest(page_url)
        if self.portal_key == "bnc_roma":
            return _build_bnc_roma_synthetic_manifest(page_url, scraped_html)
        if self.portal_key == "internetculturale_estense":
            return _build_internetculturale_estense_synthetic_manifest(page_url)
        return None

    def build_manifest_filename(self, page_url: str, container_id: str, title_slug: str) -> str:
        if self.portal_key == "biblioteca_digitale_trentina":
            bdt_id_match = re.search(r"/(?:Iconografia|Testi-a-stampa)/(\d+)", page_url, re.IGNORECASE)
            bdt_id = bdt_id_match.group(1) if bdt_id_match else container_id
            return f"manifest_bdt_{bdt_id}_{title_slug}.json"
        if self.portal_key == "biblioteca_digitale_lombarda":
            bdl_id_match = re.search(r"/bdl/public/rest/srv/item/(\d+)/pdf", page_url, re.IGNORECASE)
            bdl_id = bdl_id_match.group(1) if bdl_id_match else container_id
            return f"manifest_bdl_{bdl_id}_{title_slug}.json"
        if self.portal_key == "rovereto_digital_library":
            rovereto_id_match = re.search(
                r"/(?:entities/[a-z-]+|server/api/core/items)/([0-9a-f-]{36})",
                page_url,
                re.IGNORECASE,
            )
            rovereto_id = rovereto_id_match.group(1) if rovereto_id_match else container_id
            return f"manifest_rovereto_{rovereto_id}_{title_slug}.json"
        if self.portal_key == "doge_unige":
            doge_id_match = re.search(
                r"/(?:entities/[a-z-]+|server/api/core/items)/([0-9a-f-]{36})",
                page_url,
                re.IGNORECASE,
            )
            doge_id = doge_id_match.group(1) if doge_id_match else container_id
            return f"manifest_doge_{doge_id}_{title_slug}.json"
        return f"manifest_{container_id}_{title_slug}.json"


def _build_bdt_synthetic_manifest(page_url: str, scraped_html: str | None = None):
    try:
        from manifest_utils import build_biblioteca_digitale_trentina_synthetic_manifest
    except ImportError:  # pragma: no cover - package import path
        from src.manifest_utils import build_biblioteca_digitale_trentina_synthetic_manifest
    return build_biblioteca_digitale_trentina_synthetic_manifest(page_url, html=scraped_html)


def _build_bdl_pdf_manifest(page_url: str):
    try:
        from manifest_utils import build_biblioteca_digitale_lombarda_pdf_manifest
    except ImportError:  # pragma: no cover - package import path
        from src.manifest_utils import build_biblioteca_digitale_lombarda_pdf_manifest
    return build_biblioteca_digitale_lombarda_pdf_manifest(page_url)


def _build_rovereto_synthetic_manifest(page_url: str):
    try:
        from manifest_utils import build_rovereto_synthetic_manifest
    except ImportError:  # pragma: no cover - package import path
        from src.manifest_utils import build_rovereto_synthetic_manifest
    return build_rovereto_synthetic_manifest(page_url)


def _build_doge_synthetic_manifest(page_url: str):
    try:
        from manifest_utils import build_doge_synthetic_manifest
    except ImportError:  # pragma: no cover - package import path
        from src.manifest_utils import build_doge_synthetic_manifest
    return build_doge_synthetic_manifest(page_url)


def _build_matricula_synthetic_manifest(page_url: str, scraped_html: str | None = None):
    try:
        from manifest_utils import build_matricula_synthetic_manifest
    except ImportError:  # pragma: no cover - package import path
        from src.manifest_utils import build_matricula_synthetic_manifest
    return build_matricula_synthetic_manifest(page_url, html=scraped_html)


def _build_internet_archive_synthetic_manifest(page_url: str):
    try:
        from manifest_utils import build_ia_synthetic_manifest
    except ImportError:  # pragma: no cover - package import path
        from src.manifest_utils import build_ia_synthetic_manifest
    return build_ia_synthetic_manifest(page_url)


def _build_bnc_roma_synthetic_manifest(page_url: str, scraped_html: str | None = None):
    try:
        from manifest_utils import build_bnc_roma_synthetic_manifest
    except ImportError:  # pragma: no cover - package import path
        from src.manifest_utils import build_bnc_roma_synthetic_manifest
    return build_bnc_roma_synthetic_manifest(page_url, html=scraped_html)


def _build_internetculturale_estense_synthetic_manifest(page_url: str):
    try:
        from manifest_utils import build_internetculturale_estense_synthetic_manifest
    except ImportError:  # pragma: no cover - package import path
        from src.manifest_utils import build_internetculturale_estense_synthetic_manifest
    return build_internetculturale_estense_synthetic_manifest(page_url)


DIRECT_IMAGE_ADAPTERS_BY_CONTEXT = {
    "bnc_direct": DirectImagePortalAdapter(
        portal_label="BNC",
        referer="http://digitale.bnc.roma.sbn.it/",
    ),
    "bdt_direct": DirectImagePortalAdapter(
        portal_label="BDT",
        referer="https://bdt.bibcom.trento.it/",
    ),
    "internetculturale_cacheman_direct": DirectImagePortalAdapter(
        portal_label="InternetCulturale",
        referer="https://www.internetculturale.it/",
    ),
    "rovereto_direct": DirectImagePortalAdapter(
        portal_label="Rovereto",
        referer="https://digitallibrary.bibliotecacivica.rovereto.tn.it/",
    ),
    "doge_direct": DirectImagePortalAdapter(
        portal_label="DOGE",
        referer="https://doge.unige.net/",
    ),
}

DIRECT_IMAGE_ADAPTERS_BY_PORTAL = {
    "dl_ficlit": DirectImagePortalAdapter(
        portal_label="FICLIT",
        referer="https://dl.ficlit.unibo.it/",
    ),
}

DIRECT_IMAGE_ADAPTERS_BY_HOST_FRAGMENT = {
    "BookReaderImages.php": DirectImagePortalAdapter(
        portal_label="IA",
        referer="https://archive.org/",
        host_fragment="BookReaderImages.php",
    ),
    "hosted-images.matricula-online.eu": DirectImagePortalAdapter(
        portal_label="Matricula",
        referer="https://data.matricula-online.eu/",
        host_fragment="hosted-images.matricula-online.eu",
    ),
}

DIRECT_PDF_ADAPTERS_BY_CONTEXT = {
    "bdl_direct_pdf": DirectPdfPortalAdapter(
        portal_label="BDL",
        referer="https://www.bdl.servizirl.it/",
        default_name="documento_bdl",
    ),
}

DIRECT_PDF_ADAPTERS_BY_PORTAL = {
    "biblioteca_digitale_trentina": DirectPdfPortalAdapter(
        portal_label="BDT",
        referer="https://bdt.bibcom.trento.it/",
        default_name="documento_bdt",
    ),
}

SYNTHETIC_MANIFEST_ADAPTERS_BY_PORTAL = {
    "biblioteca_digitale_trentina": SyntheticManifestPortalAdapter(
        portal_key="biblioteca_digitale_trentina",
        portal_label="BDT",
    ),
    "biblioteca_digitale_lombarda": SyntheticManifestPortalAdapter(
        portal_key="biblioteca_digitale_lombarda",
        portal_label="BDL",
    ),
    "rovereto_digital_library": SyntheticManifestPortalAdapter(
        portal_key="rovereto_digital_library",
        portal_label="Rovereto",
    ),
    "doge_unige": SyntheticManifestPortalAdapter(
        portal_key="doge_unige",
        portal_label="DOGE",
    ),
    "matricula": SyntheticManifestPortalAdapter(
        portal_key="matricula",
        portal_label="Matricula",
    ),
    "internet_archive": SyntheticManifestPortalAdapter(
        portal_key="internet_archive",
        portal_label="IA",
    ),
    "bnc_roma": SyntheticManifestPortalAdapter(
        portal_key="bnc_roma",
        portal_label="BNC",
    ),
    "internetculturale_estense": SyntheticManifestPortalAdapter(
        portal_key="internetculturale_estense",
        portal_label="InternetCulturale",
    ),
}


def ficlit_direct_image_url_from_canvas(canvas: dict) -> str | None:
    """Estrae l'immagine diretta FICLIT dal canvas quando il tile service non e affidabile."""
    try:
        resource = canvas.get("images", [{}])[0].get("resource", {})
        image_url = (resource.get("@id") or resource.get("id") or "").strip()
        service = resource.get("service") or {}
        if isinstance(service, list):
            service = service[0] if service else {}
        service_id = (service.get("@id") or service.get("id") or "").strip() if isinstance(service, dict) else ""
        if (
            image_url.startswith("https://dl.ficlit.unibo.it/iiif/2/")
            and service_id.startswith("https://dl.ficlit.unibo.it/iiif/2/")
        ):
            return image_url
    except Exception:
        pass
    return None


def resolve_direct_image_download(portal_key: str | None, canvas: dict, service_id: str | None):
    """Restituisce (adapter, image_url) per i portali a immagine diretta supportati."""
    portal_adapter = DIRECT_IMAGE_ADAPTERS_BY_PORTAL.get(portal_key)

    if portal_adapter and portal_key == "dl_ficlit":
        image_url = ficlit_direct_image_url_from_canvas(canvas)
        if image_url:
            return portal_adapter, image_url
        return None, None

    if service_id:
        for adapter in DIRECT_IMAGE_ADAPTERS_BY_HOST_FRAGMENT.values():
            if adapter.matches_service_id(service_id):
                return adapter, service_id

    resource = canvas.get("images", [{}])[0].get("resource", {})
    service = resource.get("service") or {}
    if isinstance(service, list):
        service = service[0] if service else {}

    if isinstance(service, dict):
        adapter = DIRECT_IMAGE_ADAPTERS_BY_CONTEXT.get(service.get("@context"))
        image_url = adapter.extract_image_from_canvas(canvas, service_id) if adapter else None
        if adapter and image_url:
            return adapter, image_url

    return None, None


def _extract_pdf_url_from_entry(entry):
    if isinstance(entry, str):
        return entry if entry.lower().split("?", 1)[0].endswith(".pdf") else None
    if not isinstance(entry, dict):
        return None

    url = entry.get("@id") or entry.get("id") or entry.get("url")
    if not url:
        return None
    url_text = str(url)
    fmt = str(entry.get("format") or entry.get("type") or entry.get("profile") or "").lower()
    if url_text.lower().split("?", 1)[0].endswith(".pdf") or "pdf" in fmt:
        return url_text
    return None


def resolve_direct_pdf_download(portal_key: str | None, tiles_info=None, manifest=None):
    """Restituisce (adapter, pdf_url) per i portali a PDF diretto supportati."""
    portal_adapter = DIRECT_PDF_ADAPTERS_BY_PORTAL.get(portal_key)
    if portal_adapter:
        pdf_url = portal_adapter.extract_pdf_from_manifest(manifest)
        if pdf_url:
            return portal_adapter, pdf_url

    for canvas in tiles_info or []:
        try:
            service = canvas.get("images", [{}])[0].get("resource", {}).get("service")
        except Exception:
            continue
        services = service if isinstance(service, list) else [service]
        for svc in services:
            if not isinstance(svc, dict):
                continue
            context = svc.get("@context")
            adapter = DIRECT_PDF_ADAPTERS_BY_CONTEXT.get(context)
            if portal_adapter:
                adapter = portal_adapter or adapter
            if not adapter:
                continue
            pdf_url = adapter.extract_pdf_from_service(svc)
            if pdf_url:
                return adapter, pdf_url

    return None, None


def resolve_synthetic_manifest_download(
    portal_key: str | None,
    page_url: str,
    *,
    container_id: str,
    title_slug: str,
    scraped_html: str | None = None,
):
    """Restituisce (adapter, manifest, manifest_filename) per i portali con builder sintetico stabile."""
    adapter = SYNTHETIC_MANIFEST_ADAPTERS_BY_PORTAL.get(portal_key)
    if not adapter:
        return None, None, None

    manifest = adapter.build_manifest(page_url, scraped_html=scraped_html)
    if not manifest:
        return adapter, None, None

    manifest_filename = adapter.build_manifest_filename(page_url, container_id, title_slug)
    return adapter, manifest, manifest_filename
