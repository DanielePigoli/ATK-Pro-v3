from __future__ import annotations

from dataclasses import dataclass
from io import BytesIO

import requests
from PIL import Image


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
