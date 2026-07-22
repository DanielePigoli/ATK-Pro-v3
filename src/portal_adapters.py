from __future__ import annotations

from dataclasses import dataclass
from io import BytesIO

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


@dataclass(frozen=True)
class DirectPdfPortalAdapter:
    portal_label: str
    referer: str
    default_name: str


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


DIRECT_IMAGE_ADAPTERS_BY_CONTEXT = {
    "bdt_direct": DirectImagePortalAdapter(
        portal_label="BDT",
        referer="https://bdt.bibcom.trento.it/",
    ),
    "rovereto_direct": DirectImagePortalAdapter(
        portal_label="Rovereto",
        referer="https://digitallibrary.bibliotecacivica.rovereto.tn.it/",
    ),
}

DIRECT_IMAGE_ADAPTERS_BY_PORTAL = {
    "dl_ficlit": DirectImagePortalAdapter(
        portal_label="FICLIT",
        referer="https://dl.ficlit.unibo.it/",
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
    resource = canvas.get("images", [{}])[0].get("resource", {})
    service = resource.get("service") or {}
    if isinstance(service, list):
        service = service[0] if service else {}

    if portal_key == "dl_ficlit":
        image_url = ficlit_direct_image_url_from_canvas(canvas)
        adapter = DIRECT_IMAGE_ADAPTERS_BY_PORTAL.get(portal_key)
        if adapter and image_url:
            return adapter, image_url
        return None, None

    if isinstance(service, dict):
        adapter = DIRECT_IMAGE_ADAPTERS_BY_CONTEXT.get(service.get("@context"))
        image_url = service.get("@id") or service_id
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
    if portal_key == "biblioteca_digitale_trentina":
        adapter = DIRECT_PDF_ADAPTERS_BY_PORTAL.get(portal_key)
        if isinstance(manifest, dict):
            see_also_entries = manifest.get("seeAlso") or manifest.get("see_also") or []
            if isinstance(see_also_entries, dict):
                see_also_entries = [see_also_entries]
            for entry in see_also_entries:
                pdf_url = _extract_pdf_url_from_entry(entry)
                if adapter and pdf_url:
                    return adapter, pdf_url

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
            if portal_key == "biblioteca_digitale_trentina":
                adapter = DIRECT_PDF_ADAPTERS_BY_PORTAL.get(portal_key) or adapter
            if not adapter:
                continue
            pdf_url = svc.get("pdf_url") or _extract_pdf_url_from_entry(svc)
            if pdf_url:
                return adapter, str(pdf_url)

    return None, None
