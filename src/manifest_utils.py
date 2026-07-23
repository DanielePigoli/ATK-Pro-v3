# --- Fallback download diretto immagini BNCF (brute force) ---
import requests
def download_bncf_images_brute_force(idr, output_dir, modalita="R", seq_start=1, seq_end=None, single_seq=1, user_agent=None):
    """
    Scarica tutte le immagini disponibili per un dato idr iterando su sequence.
    modalita: "R" (registro, tutte le pagine) o "D" (documento singolo)
    seq_start/seq_end: range di pagine (solo per R)
    single_seq: pagina singola (solo per D)
    """
    os.makedirs(output_dir, exist_ok=True)
    headers = {"User-Agent": user_agent or "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    base_url = "https://teca.bncf.firenze.sbn.it/ImageViewer/servlet/ImageViewer"
    import hashlib
    def _download_image(idr, sequence, out_dir):
        params = {"idr": idr, "azione": "showImg", "sequence": sequence, "reduce": 0}
        resp = requests.get(base_url, params=params, headers=headers, stream=True, timeout=20)
        if resp.status_code == 200 and resp.headers.get("Content-Type", "").startswith("image"):
            content = resp.content
            filename = os.path.join(out_dir, f"{idr}_page_{sequence}.jpg")
            with open(filename, "wb") as f:
                f.write(content)
            # Calcola hash per rilevare placeholder
            img_hash = hashlib.md5(content).hexdigest()
            img_size = len(content)
            return True, img_hash, img_size
        return False, None, None
    if modalita.upper() == "R":
        sequence = seq_start
        found = 0
        placeholder_hash = None
        placeholder_size = None
        placeholder_count = 0
        last_hash = None
        last_size = None
        max_placeholder_repeat = 3  # Stoppa dopo 3 placeholder consecutivi
        while True:
            if seq_end is not None and sequence > seq_end:
                break
            ok, img_hash, img_size = _download_image(idr, sequence, output_dir)
            if not ok:
                if seq_end is None:
                    break  # Fine registro
                else:
                    print(f"[BNCF] Pagina {sequence} non trovata")
            else:
                # Primo placeholder: salva hash/size
                if found == 0:
                    placeholder_hash = img_hash
                    placeholder_size = img_size
                # Se hash/size identici al primo, conta come placeholder
                if img_hash == placeholder_hash and img_size == placeholder_size:
                    placeholder_count += 1
                    logger.warning(f"[BNCF] Possibile placeholder rilevato a pagina {sequence} (hash={img_hash}, size={img_size})")
                else:
                    placeholder_count = 0
                # Se troppi placeholder consecutivi, stoppa
                if placeholder_count >= max_placeholder_repeat:
                    logger.error(f"[BNCF] STOP: Rilevati {placeholder_count} placeholder consecutivi. Interrotto download per evitare inutili duplicati.")
                    break
                found += 1
                print(f"[BNCF] Scaricata pagina {sequence}")
            sequence += 1
        print(f"[BNCF] Totale immagini scaricate: {found}")
        return found
    elif modalita.upper() == "D":
        ok, img_hash, img_size = _download_image(idr, single_seq, output_dir)
        if ok:
            print(f"[BNCF] Scaricata pagina {single_seq}")
            return 1
        else:
            print(f"[BNCF] Pagina {single_seq} non trovata")
            return 0
    else:
        print("[BNCF] Modalità non riconosciuta. Usa 'R' o 'D'.")
        return 0
import requests
import re
import logging
import os
import json
from logging.handlers import RotatingFileHandler
import time
from urllib.parse import parse_qs, quote_plus, unquote_plus, urljoin, urlparse
ATKPRO_ENV = os.environ.get("ATKPRO_ENV", "development").lower()
logger = logging.getLogger(__name__)
if not logger.hasHandlers():
    handler = logging.StreamHandler()
    handler.setLevel(logging.DEBUG if ATKPRO_ENV != "production" else logging.WARNING)
    logger.addHandler(handler)
    if ATKPRO_ENV != "production":
        file_handler = RotatingFileHandler('atkpro_output.log', maxBytes=5*1024*1024, backupCount=3, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        logger.addHandler(file_handler)
logger.setLevel(logging.DEBUG if ATKPRO_ENV != "production" else logging.WARNING)

# Pacchetto di chiavi HTTP "umane", ripreso integralmente dalla v1.4.1
HEADERS_UX = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/115.0.0.0 Safari/537.36"
    ),
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "it-IT,it;q=0.9",
    "Referer": "https://antenati.cultura.gov.it/",
    "Origin": "https://antenati.cultura.gov.it",
    "Connection": "keep-alive",
}


def _origin_from_url(url: str) -> str | None:
    """Restituisce scheme://host per URL assoluti."""
    try:
        parsed = urlparse(url)
        if parsed.scheme and parsed.netloc:
            return f"{parsed.scheme}://{parsed.netloc}"
    except Exception:
        return None
    return None


def _manifest_headers(manifest_url: str, referer: str | None = None) -> dict:
    """Header HTTP per manifest IIIF.

    Per Antenati manteniamo gli header storici; per manifest diretti esterni
    evitiamo di presentarci con Origin/Referer Antenati e usiamo il dominio
    del manifest come contesto di consultazione.
    """
    headers = dict(HEADERS_UX)
    headers["Accept"] = "application/ld+json, application/json, text/plain, */*"
    if referer:
        origin = referer.rstrip("/")
        headers["Referer"] = origin + "/"
        headers["Origin"] = origin
        return headers

    origin = _origin_from_url(manifest_url)
    if origin and "antenati.cultura.gov.it" not in origin and "dam-antenati.cultura.gov.it" not in origin:
        headers["Referer"] = origin + "/"
        headers.pop("Origin", None)
    return headers


def _first_text(value, default: str = "") -> str:
    """Estrae una stringa leggibile da label/value IIIF v2/v3."""
    if value is None:
        return default
    if isinstance(value, str):
        return value
    if isinstance(value, list):
        parts = [_first_text(item, "") for item in value]
        return " ".join(part for part in parts if part) or default
    if isinstance(value, dict):
        for key in ("it", "en", "de", "fr", "none", "@value", "value"):
            if key in value:
                text = _first_text(value.get(key), "")
                if text:
                    return text
        for item in value.values():
            text = _first_text(item, "")
            if text:
                return text
    return default


def extract_manifest_url_from_viewer_url(page_url: str) -> str | None:
    """Estrae un manifest IIIF da URL viewer che lo contengono in query.

    Copre Mirador e viewer simili che usano parametri come manifestId o manifest.
    """
    try:
        parsed = urlparse(page_url)
        query = parse_qs(parsed.query or "")
    except Exception:
        return None

    for key in ("manifestId", "manifest", "iiif-content", "iiif_manifest"):
        values = query.get(key)
        if values:
            candidate = unquote_plus(values[0]).strip()
            if candidate.startswith(("http://", "https://")):
                return candidate
    return None


def _normalize_v3_service(service):
    if isinstance(service, list):
        return [_normalize_v3_service(item) for item in service if isinstance(item, dict)]
    if not isinstance(service, dict):
        return service

    service_id = service.get("@id") or service.get("id")
    service_type = service.get("@type") or service.get("type")
    normalized = {
        "@id": service_id,
        "@type": service_type or "ImageService3",
    }
    for key in ("profile", "width", "height", "tiles", "sizes"):
        if key in service:
            normalized[key] = service[key]
    if service.get("@context"):
        normalized["@context"] = service["@context"]
    elif service_type == "ImageService3" or str(service.get("profile", "")).find("/image/3/") >= 0:
        normalized["@context"] = "http://iiif.io/api/image/3/context.json"
    return {key: value for key, value in normalized.items() if value is not None}


def _find_v3_image_body(canvas: dict) -> dict | None:
    for page in canvas.get("items", []) or []:
        for annotation in page.get("items", []) or []:
            motivation = annotation.get("motivation")
            if motivation and motivation != "painting":
                continue
            body = annotation.get("body")
            bodies = body if isinstance(body, list) else [body]
            for candidate in bodies:
                if isinstance(candidate, dict) and candidate.get("type") in (None, "Image", "dctypes:Image"):
                    return candidate
    return None


def _normalize_metadata_entries(metadata):
    if not isinstance(metadata, list):
        return metadata or []
    normalized = []
    for entry in metadata:
        if not isinstance(entry, dict):
            continue
        normalized.append(
            {
                "label": _first_text(entry.get("label"), ""),
                "value": _first_text(entry.get("value"), ""),
            }
        )
    return normalized


def normalize_iiif_manifest_for_processing(manifest: dict) -> dict:
    """Converte manifest IIIF Presentation v3 image-only in layout v2 interno.

    La pipeline di ATK-Pro lavora ancora su sequences/canvases; questa funzione
    permette di supportare i manifest v3 senza riscrivere il motore di download.
    I manifest v2 o sintetici esistenti vengono restituiti invariati.
    """
    if not isinstance(manifest, dict):
        return manifest
    if manifest.get("sequences"):
        return manifest
    if manifest.get("type") != "Manifest" or not isinstance(manifest.get("items"), list):
        return manifest

    canvases = []
    for index, canvas in enumerate(manifest.get("items", []), 1):
        if not isinstance(canvas, dict) or canvas.get("type") != "Canvas":
            continue
        body = _find_v3_image_body(canvas)
        if not body:
            continue

        canvas_id = canvas.get("id") or f"canvas-{index}"
        image_id = body.get("id") or body.get("@id")
        service = _normalize_v3_service(body.get("service"))
        width = body.get("width") or canvas.get("width")
        height = body.get("height") or canvas.get("height")

        resource = {
            "@id": image_id,
            "@type": "dctypes:Image",
            "format": body.get("format"),
            "width": width,
            "height": height,
            "service": service,
        }
        resource = {key: value for key, value in resource.items() if value is not None}

        canvases.append(
            {
                "@id": canvas_id,
                "@type": "sc:Canvas",
                "label": _first_text(canvas.get("label"), f"Canvas {index}"),
                "width": width,
                "height": height,
                "images": [
                    {
                        "@type": "oa:Annotation",
                        "motivation": "sc:painting",
                        "resource": resource,
                        "on": canvas_id,
                    }
                ],
            }
        )

    if not canvases:
        return manifest

    normalized = {
        "@context": "http://iiif.io/api/presentation/2/context.json",
        "@id": manifest.get("id") or manifest.get("@id"),
        "@type": "sc:Manifest",
        "label": _first_text(manifest.get("label"), "Manifest IIIF v3"),
        "metadata": _normalize_metadata_entries(manifest.get("metadata")),
        "sequences": [
            {
                "@type": "sc:Sequence",
                "canvases": canvases,
            }
        ],
        "_atk_normalized_from_iiif_v3": True,
    }
    if manifest.get("rights"):
        normalized["rights"] = manifest["rights"]
    return {key: value for key, value in normalized.items() if value is not None}

# Regex permissive v1.4.1 per intercettare il manifest nel DOM/HTML
_RE_MANIFEST_ANY = re.compile(
    r"https://dam-antenati\.cultura\.gov\.it/antenati/containers/[A-Za-z0-9]+/manifest"
)
# Supporto anche a varianti accidentalmente espanse
_RE_MANIFEST_JSON = re.compile(
    r"https://dam-antenati\.cultura\.gov\.it/antenati/containers/[A-Za-z0-9]+/manifest\.json"
)

def _find_manifest_in_html(html: str) -> str | None:
    """
    Cerca il manifest direttamente nell'HTML, replicando la logica v1.4.1.
    """
    if not html:
        return None
    # Preferiamo link che includono esplicitamente '.json' se presenti
    m = _RE_MANIFEST_JSON.search(html)
    if m:
        manifest_url = m.group(0)
        print(f"[Manifest] Trovato: {manifest_url}")
        return manifest_url
    # Poi la variante v1.4.1 classica (containers/.../manifest)
    m = _RE_MANIFEST_ANY.search(html)
    if m:
        manifest_url = m.group(0)
        print(f"[Manifest] Trovato: {manifest_url}")
        return manifest_url
    # Accetta anche link relativi come href="manifest.json" o "/manifest.json"
    m = re.search(r'href=[\"\']([^\"\']*manifest(?:\.json)?)[\"\']', html, re.IGNORECASE)
    if m:
        manifest_url = m.group(1)
        print(f"[Manifest] Trovato (relativo): {manifest_url}")
        return manifest_url
    return None

def _http_get(url: str, timeout: int = 20) -> requests.Response | None:
    """
    GET con HEADERS_UX completi (v1.4.1), indispensabili per 'aprire' il portale.
    """
    try:
        r = requests.get(url, headers=HEADERS_UX, timeout=timeout)
        logger.debug(f"GET {url} -> {r.status_code}")
        return r
    except Exception as e:
        logger.warning(f"[HTTP] Errore GET {url}: {e}")
        return None


# ──────────────────────────────────────────────────────────────────
# Builder URL manifest per portali IIIF supportati (Layer 1)
# ──────────────────────────────────────────────────────────────────

def _build_gallica_manifest(page_url: str) -> str | None:
    """Gallica BnF: .../ark:/12148/{id} → .../iiif/ark:/12148/{id}/manifest.json"""
    m = re.search(r'gallica\.bnf\.fr(.*/ark:/12148/[A-Za-z0-9]+)', page_url)
    if m:
        return f"https://gallica.bnf.fr/iiif{m.group(1)}/manifest.json"
    return None


def _build_vatlib_manifest(page_url: str) -> str | None:
    """DigiVatLib (Biblioteca Apostolica Vaticana):
    /view/{MSS_ID} o /mss/edition/{MSS_ID} → /iiif/{MSS_ID}/manifest.json
    Accetta anche URL manifest già completo (/iiif/{MSS_ID}/manifest.json).
    """
    # Già un manifest IIIF VAT
    if '/iiif/' in page_url and 'manifest.json' in page_url:
        m = re.search(r'digi\.vatlib\.it/iiif/([^/]+)/manifest\.json', page_url)
        if m:
            return page_url
    # URL viewer /view/{ID} o /mss/edition/{ID}
    m = re.search(r'digi\.vatlib\.it/(?:view|mss/edition)/([^/?#\s]+)', page_url)
    if m:
        mss_id = m.group(1)
        return f"https://digi.vatlib.it/iiif/{mss_id}/manifest.json"
    # URL IIIF senza manifest.json (e.g. /iiif/{ID})
    m = re.search(r'digi\.vatlib\.it/iiif/([^/?#\s]+)', page_url)
    if m:
        mss_id = m.group(1)
        return f"https://digi.vatlib.it/iiif/{mss_id}/manifest.json"
    return None


def _build_bodleian_manifest(page_url: str) -> str | None:
    """Bodleian Libraries Oxford:
    /objects/{uuid}/ → https://iiif.bodleian.ox.ac.uk/iiif/manifest/{uuid}.json
    """
    m = re.search(r'digital\.bodleian\.ox\.ac\.uk/objects/([^/?#\s]+)', page_url)
    if m:
        uuid = m.group(1)
        return f"https://iiif.bodleian.ox.ac.uk/iiif/manifest/{uuid}.json"
    return None


def _build_europeana_manifest(page_url: str) -> str | None:
    """Europeana IIIF:
    /en/item/{provider_id}/{record_id} → /presentation/{provider_id}/{record_id}/manifest
    """
    m = re.search(r'europeana\.eu/(?:[a-z]{2}/)?item/([^/]+)/([^/?#\s]+)', page_url)
    if m:
        provider_id = m.group(1)
        record_id = m.group(2)
        return f"https://iiif.europeana.eu/presentation/{provider_id}/{record_id}/manifest"
    return None


def _build_ia_manifest(page_url: str) -> str | None:
    """Internet Archive: restituisce un placeholder URL riconoscibile; il manifest
    sintetico viene costruito da build_ia_synthetic_manifest() in elaborazione."""
    m = re.search(r'archive\.org/(?:details|stream|download)/([A-Za-z0-9._-]+)', page_url)
    if m:
        return f"https://iiif.archivelab.org/iiif/{m.group(1)}/manifest.json"
    return None


def build_ia_synthetic_manifest(page_url: str) -> dict | None:
    """
    Costruisce un manifest IIIF sintetico per un item di Internet Archive usando:
      - archive.org/metadata/{item_id}  → server, dir, file list
      - {server}{dir}/{item_id}_page_numbers.json → conteggio pagine
      - BookReaderImages.php  → URL immagine per ogni pagina

    Il manifest prodotto usa 'ia_direct' come contesto del service, riconoscibile
    da download_ia_page() in elaborazione.py per il download diretto senza tile.
    """
    m = re.search(r'archive\.org/(?:details|stream|download)/([A-Za-z0-9._-]+)', page_url)
    if not m:
        logger.error(f"[IA] URL non riconoscibile: {page_url}")
        return None
    item_id = m.group(1)

    try:
        _h = dict(HEADERS_UX)
        meta_r = requests.get(f'https://archive.org/metadata/{item_id}', headers=_h, timeout=15)
        meta_r.raise_for_status()
        data = meta_r.json()
    except Exception as e:
        logger.error(f"[IA] Metadata API fallita per {item_id}: {e}")
        return None

    server = data.get('server', '')
    dir_ = data.get('dir', '')
    files = data.get('files', [])
    item_meta = data.get('metadata', {})

    if not server or not dir_:
        logger.error(f"[IA] Metadati incompleti per {item_id}: server={server!r} dir={dir_!r}")
        return None

    # Trova JP2 ZIP (non-raw, primo disponibile)
    jp2_zip = next(
        (f for f in files
         if f.get('name', '').endswith('_jp2.zip') and 'raw' not in f.get('name', '')),
        None
    )
    if not jp2_zip:
        logger.error(f"[IA] Nessun JP2 ZIP trovato per {item_id}")
        return None

    zip_name = jp2_zip['name'].replace('_jp2.zip', '')
    zip_path = dir_ + '/' + jp2_zip['name']

    # Conta le pagine tramite page_numbers.json
    pn_file = next((f for f in files if f.get('name', '').endswith('_page_numbers.json')), None)
    num_pages = 0
    if pn_file:
        try:
            pn_r = requests.get(
                f'https://{server}{dir_}/{pn_file["name"]}', headers=_h, timeout=12
            )
            if pn_r.ok:
                num_pages = len(pn_r.json().get('pages', []))
        except Exception as e:
            logger.warning(f"[IA] page_numbers.json non disponibile: {e}")

    if num_pages == 0:
        logger.error(f"[IA] Impossibile determinare numero pagine per {item_id}")
        return None

    title = item_meta.get('title', item_id)
    if isinstance(title, list):
        title = title[0]

    def _make_ia_canvas(page_num: int) -> dict:
        page_file = f'{zip_name}_jp2/{zip_name}_{str(page_num).zfill(4)}.jp2'
        img_url = (
            f'https://{server}/BookReader/BookReaderImages.php'
            f'?zip={zip_path}&file={page_file}&id={item_id}&scale=1&rotate=0'
        )
        return {
            '@id': f'https://archive.org/bookreader/{item_id}/canvas/{page_num}',
            '@type': 'sc:Canvas',
            'label': f'Page {page_num}',
            'width': 800,
            'height': 1200,
            'images': [{
                '@type': 'oa:Annotation',
                'motivation': 'sc:painting',
                'resource': {
                    '@type': 'dctypes:Image',
                    '@id': img_url,
                    'format': 'image/jpeg',
                    'service': {
                        '@context': 'ia_direct',
                        '@id': img_url,
                        'profile': 'ia_direct'
                    }
                }
            }]
        }

    canvases = [_make_ia_canvas(i) for i in range(1, num_pages + 1)]
    logger.info(f"[IA] Manifest sintetico costruito: {item_id}, {num_pages} pagine")

    return {
        '@context': 'http://iiif.io/api/presentation/2/context.json',
        '@id': f'https://archive.org/details/{item_id}',
        '@type': 'sc:Manifest',
        'label': title,
        'sequences': [{
            '@type': 'sc:Sequence',
            'canvases': canvases
        }]
    }


def _build_ecodices_manifest(page_url: str) -> str | None:
    """e-codices: sia /en/{lib}/{id}/ che /list/one/{lib}/{id} → .../metadata/iiif/{lib}-{id}/manifest.json"""
    # Formato viewer: /en/csg/0390/1r/max  oppure  /list/one/csg/0390
    m = re.search(
        r'e-codices\.unifr\.ch/(?:[a-z]+/[a-z]+/one/|[a-z]{2}/)([A-Za-z0-9]+)/([A-Za-z0-9-]+)',
        page_url
    )
    if m:
        doc_id = f"{m.group(1)}-{m.group(2)}"
        return f"https://www.e-codices.unifr.ch/metadata/iiif/{doc_id}/manifest.json"
    return None


def _build_heidelberg_manifest(page_url: str) -> str | None:
    """Heidelberg UB: .../diglit/{id} → .../diglit/iiif/{id}/manifest.json (IIIF v2)"""
    m = re.search(r'digi\.ub\.uni-heidelberg\.de/diglit/(?:iiif/)?([A-Za-z0-9_.-]+)', page_url)
    if m:
        doc_id = m.group(1)
        return f"https://digi.ub.uni-heidelberg.de/diglit/iiif/{doc_id}/manifest.json"
    return None


def _build_e_manuscripta_manifest(page_url: str) -> str | None:
    """e-manuscripta: .../content/titleinfo/{id} (o URL breve .../{id}) → /i3f/v20/{id}/manifest"""
    m = re.search(r'e-manuscripta\.ch/(?:[^?#]*/)?content/titleinfo/(\d+)', page_url, re.IGNORECASE)
    if not m:
        m = re.search(r'e-manuscripta\.ch/[^?#]*/(\d+)(?:[/?#]|$)', page_url, re.IGNORECASE)
    if m:
        doc_id = m.group(1)
        return f"https://www.e-manuscripta.ch/i3f/v20/{doc_id}/manifest"
    return None


def _build_e_rara_manifest(page_url: str) -> str | None:
    """e-rara: /content/titleinfo/{id} → /i3f/v20/{id}/manifest.
    Supporta anche URL brevi /{id}, risolvendo l'ID publication dalla pagina.
    """
    m = re.search(r'e-rara\.ch/(?:[^?#]*/)?content/titleinfo/(\d+)', page_url, re.IGNORECASE)
    if not m:
        short_m = re.search(r'e-rara\.ch/(\d+)(?:[/?#]|$)', page_url, re.IGNORECASE)
        if short_m:
            short_url = f"https://www.e-rara.ch/{short_m.group(1)}"
            r = _http_get(short_url, timeout=20)
            if r and r.ok:
                html = r.text or ""
                m = re.search(r'publicationID"\s+value="(\d+)"', html)
                if not m:
                    m = re.search(r'/content/titleinfo/(\d+)', html)
    if m:
        doc_id = m.group(1)
        return f"https://www.e-rara.ch/i3f/v20/{doc_id}/manifest"
    return None


def _build_biblioteca_digitale_siena_manifest(page_url: str) -> str | None:
    """Biblioteca Digitale Siena:
    /it/vieweriiif/?id={id}&type={type} -> /metadata/{id}/manifest.json?type={type}
    """
    parsed = urlparse(page_url)
    if not parsed.netloc.lower().endswith("bds.comune.siena.it"):
        return None

    query = parse_qs(parsed.query or "")
    doc_id = (query.get("id") or [""])[0].strip()
    doc_type = (query.get("type") or ["sbn"])[0].strip() or "sbn"
    if not doc_id:
        return None

    return f"https://bds.comune.siena.it/metadata/{doc_id}/manifest.json?type={quote_plus(doc_type)}"


def _build_bub_digitale_manifest(page_url: str) -> str | None:
    """BUB Digitale: pagine viewer con parametro manifest -> URL manifest IIIF diretto."""
    parsed = urlparse(page_url)
    if not parsed.netloc.lower().endswith("bub.unibo.it"):
        return None

    query = parse_qs(parsed.query or "")
    manifest = (query.get("manifest") or query.get("manifestId") or [""])[0].strip()
    if manifest and manifest.startswith("https://bub.unibo.it/iiif/2/manifest/"):
        return manifest

    if page_url.startswith("https://bub.unibo.it/iiif/2/manifest/"):
        return page_url
    return None


def _build_dl_ficlit_manifest(page_url: str) -> str | None:
    """DL FICLIT: item Omeka S o manifest IIIF v2 diretto sul dominio FICLIT."""
    parsed = urlparse(page_url)
    if parsed.netloc.lower() != "dl.ficlit.unibo.it":
        return None

    path = parsed.path.rstrip("/")
    direct_match = re.fullmatch(r"/iiif/2/(\d+)/manifest", path, re.IGNORECASE)
    if direct_match:
        return f"https://dl.ficlit.unibo.it/iiif/2/{direct_match.group(1)}/manifest"

    item_match = re.fullmatch(r"/s/lib/item/(\d+)", path, re.IGNORECASE)
    if item_match:
        return f"https://dl.ficlit.unibo.it/iiif/2/{item_match.group(1)}/manifest"

    query = parse_qs(parsed.query or "")
    manifest = (query.get("manifest") or query.get("manifestId") or [""])[0].strip()
    manifest_parsed = urlparse(manifest)
    if (
        manifest
        and manifest_parsed.netloc.lower() == "dl.ficlit.unibo.it"
        and re.fullmatch(r"/iiif/2/\d+/manifest", manifest_parsed.path.rstrip("/"), re.IGNORECASE)
    ):
        return manifest

    return None


_BDT_ATTR_URL_RE = re.compile(
    r"""(?ix)
    \b(?:href|src|data-[a-z0-9_-]+|content)\s*=\s*
    (?P<quote>["'])
    (?P<url>[^"']+)
    (?P=quote)
    """
)
_BDT_ABSOLUTE_URL_RE = re.compile(r"https?://[^\s\"'<>\\)]+", re.IGNORECASE)


def _bdt_is_supported_url(page_url: str) -> bool:
    parsed = urlparse(page_url)
    host = parsed.netloc.lower()
    return host.endswith("bdt.bibcom.trento.it")


def _build_biblioteca_digitale_trentina_manifest(page_url: str) -> str | None:
    """Biblioteca Digitale Trentina: pagina item-level gestita via manifest sintetico."""
    if not _bdt_is_supported_url(page_url):
        return None
    if re.search(r"/(?:Iconografia|Testi-a-stampa)/\d+", urlparse(page_url).path, re.IGNORECASE):
        return page_url
    return None


def _bdt_clean_url(raw: str, base_url: str) -> str | None:
    value = raw.strip()
    if not value or value.startswith(("#", "javascript:", "mailto:", "tel:")):
        return None
    return urljoin(base_url, value)


def _bdt_image_role(url: str) -> str | None:
    lowered = url.lower()
    path = urlparse(url).path.lower()
    if not path.endswith((".jpg", ".jpeg", ".png", ".webp", ".tif", ".tiff")):
        return None
    if any(token in lowered for token in ("_header_logo", "/header", "/logo", "favicon")):
        return "site_asset"
    if any(token in lowered for token in ("/media/immagini-", "_large.", "/storage/images/media/")):
        return "content_image"
    return "image_candidate"


def _bdt_page_number(url: str) -> int | None:
    match = re.search(r"(?:^|/)page-(\d+)\.jpe?g", url, re.IGNORECASE)
    return int(match.group(1)) if match else None


def _bdt_image_group_key(url: str) -> tuple[str, int | str]:
    page_number = _bdt_page_number(url)
    if page_number is not None:
        return ("page", page_number)
    filename = urlparse(url).path.rsplit("/", 1)[-1].lower().replace("_large.", ".")
    return ("image", filename)


def _bdt_prefer_image_variant(existing: str | None, candidate: str) -> str:
    if existing is None:
        return candidate
    existing_large = "_large." in existing.lower()
    candidate_large = "_large." in candidate.lower()
    if candidate_large and not existing_large:
        return candidate
    if candidate_large == existing_large and len(candidate) > len(existing):
        return candidate
    return existing


def _bdt_image_sort_key(url: str) -> tuple[int, int, str]:
    page_number = _bdt_page_number(url)
    variant_rank = 1 if "_large." in url.lower() else 0
    return (page_number if page_number is not None else 10**9, variant_rank, url)


def _extract_bdt_content_image_urls(html: str, base_url: str) -> list[str]:
    raw_urls: list[str] = []
    raw_urls.extend(match.group("url") for match in _BDT_ATTR_URL_RE.finditer(html))
    raw_urls.extend(match.group(0) for match in _BDT_ABSOLUTE_URL_RE.finditer(html))

    grouped: dict[tuple[str, int | str], str] = {}
    for raw in raw_urls:
        normalized = _bdt_clean_url(raw, base_url)
        if not normalized:
            continue
        if _bdt_image_role(normalized) != "content_image":
            continue
        group_key = _bdt_image_group_key(normalized)
        grouped[group_key] = _bdt_prefer_image_variant(grouped.get(group_key), normalized)

    return sorted(grouped.values(), key=_bdt_image_sort_key)


def _extract_bdt_pdf_url(html: str, base_url: str) -> str | None:
    for match in _BDT_ATTR_URL_RE.finditer(html):
        normalized = _bdt_clean_url(match.group("url"), base_url)
        if not normalized:
            continue
        parsed = urlparse(normalized)
        if parsed.path.lower().endswith(".pdf"):
            return normalized
    return None


def build_biblioteca_digitale_trentina_synthetic_manifest(
    page_url: str,
    html: str | None = None,
) -> dict | None:
    """Costruisce un manifest sintetico BDT da immagini JPEG pubbliche in pagina."""
    if not _bdt_is_supported_url(page_url):
        return None

    if html is None:
        response = _http_get(page_url, timeout=25)
        if not response or not response.ok:
            logger.error(f"[BDT] Impossibile scaricare pagina: {page_url}")
            return None
        html = response.text or ""

    image_urls = _extract_bdt_content_image_urls(html, page_url)
    if not image_urls:
        logger.error(f"[BDT] Nessuna immagine di contenuto trovata: {page_url}")
        return None

    title_match = re.search(r"<h1[^>]*>(.*?)</h1>", html, re.IGNORECASE | re.DOTALL)
    if not title_match:
        title_match = re.search(r"<title[^>]*>(.*?)</title>", html, re.IGNORECASE | re.DOTALL)
    title = re.sub(r"\s+", " ", title_match.group(1)).strip() if title_match else page_url
    title = re.sub(r"<[^>]+>", "", title).strip() or page_url

    pdf_url = _extract_bdt_pdf_url(html, page_url)
    safe_id_match = re.search(r"/(?:Iconografia|Testi-a-stampa)/(\d+)", urlparse(page_url).path, re.IGNORECASE)
    safe_id = safe_id_match.group(1) if safe_id_match else re.sub(r"[^A-Za-z0-9._-]+", "_", page_url)

    canvases = []
    for idx, img_url in enumerate(image_urls, start=1):
        page_number = _bdt_page_number(img_url) or idx
        label = f"Pagina {page_number}" if _bdt_page_number(img_url) else f"Immagine {idx}"
        canvases.append({
            '@id': f"synthetic://biblioteca_digitale_trentina/{safe_id}/canvas/{idx}",
            '@type': 'sc:Canvas',
            'label': label,
            'images': [{
                '@type': 'oa:Annotation',
                'motivation': 'sc:painting',
                'resource': {
                    '@type': 'dctypes:Image',
                    '@id': img_url,
                    'format': 'image/jpeg',
                    'service': {
                        '@context': 'bdt_direct',
                        '@id': img_url,
                        'profile': 'bdt_direct',
                        'source_page': page_url,
                        'pdf_url': pdf_url,
                    }
                }
            }]
        })

    logger.info(f"[BDT] Manifest sintetico: '{title}', {len(canvases)} immagini")
    return {
        '@context': 'http://iiif.io/api/presentation/2/context.json',
        '@id': f"synthetic://biblioteca_digitale_trentina/{safe_id}",
        '@type': 'sc:Manifest',
        'label': title,
        'seeAlso': [{'@id': pdf_url, 'format': 'application/pdf'}] if pdf_url else [],
        'sequences': [{
            '@id': f"synthetic://biblioteca_digitale_trentina/{safe_id}/sequence/1",
            '@type': 'sc:Sequence',
            'canvases': canvases,
        }],
    }


def _bdl_is_supported_url(page_url: str) -> bool:
    parsed = urlparse(page_url)
    return parsed.netloc.lower().endswith("bdl.servizirl.it")


def _bdl_extract_pdf_item_id(page_url: str) -> str | None:
    parsed = urlparse(page_url)
    match = re.search(r"/bdl/public/rest/srv/item/(\d+)/pdf\b", parsed.path, re.IGNORECASE)
    return match.group(1) if match else None


def _build_biblioteca_digitale_lombarda_manifest(page_url: str) -> str | None:
    """Biblioteca Digitale Lombarda: solo endpoint PDF REST pubblico."""
    if not _bdl_is_supported_url(page_url):
        return None
    return page_url if _bdl_extract_pdf_item_id(page_url) else None


def build_biblioteca_digitale_lombarda_pdf_manifest(pdf_url: str) -> dict | None:
    """Costruisce un manifest sintetico minimale per un PDF pubblico BDL."""
    item_id = _bdl_extract_pdf_item_id(pdf_url)
    if not item_id:
        return None

    return {
        "@context": "http://iiif.io/api/presentation/2/context.json",
        "@id": f"synthetic://biblioteca_digitale_lombarda/{item_id}",
        "@type": "sc:Manifest",
        "label": f"Biblioteca Digitale Lombarda - item {item_id}",
        "metadata": [
            {"label": "Portale", "value": "Biblioteca Digitale Lombarda"},
            {"label": "PDF REST", "value": pdf_url},
        ],
        "seeAlso": [{"@id": pdf_url, "format": "application/pdf"}],
        "sequences": [
            {
                "@id": f"synthetic://biblioteca_digitale_lombarda/{item_id}/sequence/1",
                "@type": "sc:Sequence",
                "canvases": [
                    {
                        "@id": f"synthetic://biblioteca_digitale_lombarda/{item_id}/canvas/1",
                        "@type": "sc:Canvas",
                        "label": "PDF diretto",
                        "images": [
                            {
                                "@type": "oa:Annotation",
                                "motivation": "sc:painting",
                                "resource": {
                                    "@type": "dctypes:Image",
                                    "@id": pdf_url,
                                    "format": "application/pdf",
                                    "service": {
                                        "@context": "bdl_direct_pdf",
                                        "@id": pdf_url,
                                        "profile": "bdl_direct_pdf",
                                        "pdf_url": pdf_url,
                                    },
                                },
                            }
                        ],
                    }
                ],
            }
        ],
    }


def _rovereto_is_supported_url(page_url: str) -> bool:
    parsed = urlparse(page_url)
    return parsed.netloc.lower().endswith("digitallibrary.bibliotecacivica.rovereto.tn.it")


def _rovereto_extract_item_uuid(page_url: str) -> str | None:
    parsed = urlparse(page_url)
    match = re.search(
        r"/(?:entities/[a-z-]+|server/api/core/items)/"
        r"([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})\b",
        parsed.path,
        re.IGNORECASE,
    )
    return match.group(1) if match else None


def _rovereto_item_api_url(page_url: str) -> str | None:
    if not _rovereto_is_supported_url(page_url):
        return None
    item_uuid = _rovereto_extract_item_uuid(page_url)
    if not item_uuid:
        return None
    parsed = urlparse(page_url)
    return f"{parsed.scheme}://{parsed.netloc}/server/api/core/items/{item_uuid}"


def _build_rovereto_manifest(page_url: str) -> str | None:
    """Rovereto Digital Library: item DSpace-GLAM gestito via manifest sintetico."""
    return page_url if _rovereto_item_api_url(page_url) else None


def _rovereto_headers() -> dict:
    return {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "it-IT,it;q=0.9,en;q=0.7",
        "Referer": "https://digitallibrary.bibliotecacivica.rovereto.tn.it/",
    }


def _rovereto_get_json(url: str, timeout: int = 25) -> dict | None:
    try:
        response = requests.get(url, headers=_rovereto_headers(), timeout=timeout)
        logger.debug(f"[Rovereto] GET {url} -> {response.status_code}")
        if not response.ok:
            return None
        data = response.json()
        return data if isinstance(data, dict) else None
    except Exception as exc:
        logger.warning(f"[Rovereto] Errore JSON {url}: {exc}")
        return None


def _rovereto_link(data: dict, name: str) -> str | None:
    links = data.get("_links")
    if not isinstance(links, dict):
        return None
    entry = links.get(name)
    if not isinstance(entry, dict):
        return None
    href = entry.get("href")
    return str(href) if href else None


def _rovereto_embedded_items(data: dict, key: str) -> list[dict]:
    embedded = data.get("_embedded")
    if not isinstance(embedded, dict):
        return []
    values = embedded.get(key)
    if not isinstance(values, list):
        return []
    return [item for item in values if isinstance(item, dict)]


def _rovereto_collect_paginated_items(first_url: str, key: str, max_pages: int = 50) -> list[dict]:
    items: list[dict] = []
    seen: set[str] = set()
    next_url: str | None = first_url
    while next_url and next_url not in seen and len(seen) < max_pages:
        seen.add(next_url)
        data = _rovereto_get_json(next_url)
        if not data:
            break
        items.extend(_rovereto_embedded_items(data, key))
        next_url = _rovereto_link(data, "next")
    if next_url and next_url not in seen:
        logger.warning(f"[Rovereto] Paginazione interrotta dopo {max_pages} pagine: {first_url}")
    return items


def _rovereto_first_metadata_value(data: dict, key: str) -> str | None:
    metadata = data.get("metadata")
    if not isinstance(metadata, dict):
        return None
    values = metadata.get(key)
    if not isinstance(values, list):
        return None
    for entry in values:
        if not isinstance(entry, dict):
            continue
        value = entry.get("value")
        if value:
            return str(value)
    return None


def _rovereto_page_number(name: str) -> int | None:
    match = re.fullmatch(r"iiifpdf-(\d+)\.png", name.lower())
    return int(match.group(1)) + 1 if match else None


def _rovereto_bitstream_category(name: str, mimetype: str) -> tuple[str, str, int | None]:
    name_lower = name.lower()
    mimetype_lower = mimetype.lower()
    page_number = _rovereto_page_number(name)
    if page_number is not None and mimetype_lower == "image/png":
        return "page_image", "yes", page_number
    if mimetype_lower == "application/pdf" or name_lower.endswith(".pdf"):
        return "source_pdf", "yes", None
    if name_lower == "license.txt":
        return "license", "no", None
    if name_lower.endswith(".txt") or mimetype_lower.startswith("text/plain"):
        return "text_derivative", "no", None
    if name_lower.endswith((".jpg", ".jpeg")) and mimetype_lower == "image/jpeg":
        return "thumbnail_or_cover", "no", None
    if mimetype_lower.startswith("image/"):
        return "image_other", "review", None
    return "other", "review", None


def _rovereto_format_mimetype(bitstream: dict) -> str:
    embedded_format = bitstream.get("format")
    if isinstance(embedded_format, dict):
        return str(embedded_format.get("mimetype") or "")
    format_url = _rovereto_link(bitstream, "format")
    if not format_url:
        return ""
    format_data = _rovereto_get_json(format_url)
    if not format_data:
        return ""
    return str(format_data.get("mimetype") or "")


def _rovereto_collect_bitstreams(item_data: dict) -> list[dict]:
    bundles_url = _rovereto_link(item_data, "bundles")
    if not bundles_url:
        return []

    bitstreams: list[dict] = []
    for bundle in _rovereto_collect_paginated_items(bundles_url, "bundles"):
        bitstreams_url = _rovereto_link(bundle, "bitstreams")
        if not bitstreams_url:
            continue
        bitstreams.extend(_rovereto_collect_paginated_items(bitstreams_url, "bitstreams"))
    return bitstreams


def build_rovereto_synthetic_manifest(page_url: str) -> dict | None:
    """Costruisce un manifest sintetico Rovereto da bitstream DSpace pubblici."""
    item_api_url = _rovereto_item_api_url(page_url)
    if not item_api_url:
        return None

    item_data = _rovereto_get_json(item_api_url)
    if not item_data:
        logger.error(f"[Rovereto] Impossibile leggere item API: {item_api_url}")
        return None

    title = (
        str(item_data.get("name") or "")
        or _rovereto_first_metadata_value(item_data, "dc.title")
        or page_url
    )
    item_uuid = str(item_data.get("uuid") or _rovereto_extract_item_uuid(page_url) or "item")

    page_entries: list[dict] = []
    source_pdf_url = None
    for bitstream in _rovereto_collect_bitstreams(item_data):
        name = str(bitstream.get("name") or "")
        mimetype = _rovereto_format_mimetype(bitstream)
        category, download_candidate, page_number = _rovereto_bitstream_category(name, mimetype)
        content_url = _rovereto_link(bitstream, "content")
        if not content_url:
            continue
        if category == "source_pdf" and not source_pdf_url:
            source_pdf_url = content_url
        if category != "page_image" or download_candidate != "yes" or page_number is None:
            continue
        page_entries.append(
            {
                "page_number": page_number,
                "name": name,
                "content_url": content_url,
                "uuid": str(bitstream.get("uuid") or ""),
                "size_bytes": bitstream.get("sizeBytes"),
            }
        )

    page_entries = sorted(page_entries, key=lambda entry: (entry["page_number"], entry["name"]))
    if not page_entries:
        logger.error(f"[Rovereto] Nessuna pagina immagine pubblica trovata: {page_url}")
        return None

    expected_pages = set(range(page_entries[0]["page_number"], page_entries[-1]["page_number"] + 1))
    actual_pages = {entry["page_number"] for entry in page_entries}
    if expected_pages != actual_pages:
        missing = sorted(expected_pages - actual_pages)
        logger.warning(f"[Rovereto] Sequenza pagine non continua; mancanti: {missing}")

    canvases = []
    for idx, entry in enumerate(page_entries, start=1):
        page_number = entry["page_number"]
        img_url = entry["content_url"]
        canvases.append(
            {
                "@id": f"synthetic://rovereto_digital_library/{item_uuid}/canvas/{page_number}",
                "@type": "sc:Canvas",
                "label": f"Pagina {page_number}",
                "images": [
                    {
                        "@type": "oa:Annotation",
                        "motivation": "sc:painting",
                        "resource": {
                            "@type": "dctypes:Image",
                            "@id": img_url,
                            "format": "image/png",
                            "service": {
                                "@context": "rovereto_direct",
                                "@id": img_url,
                                "profile": "rovereto_direct",
                                "source_page": page_url,
                                "item_api_url": item_api_url,
                                "bitstream_uuid": entry["uuid"],
                                "page_number": page_number,
                                "size_bytes": entry.get("size_bytes"),
                            },
                        },
                    }
                ],
            }
        )

    logger.info(f"[Rovereto] Manifest sintetico: '{title}', {len(canvases)} pagine")
    return {
        "@context": "http://iiif.io/api/presentation/2/context.json",
        "@id": f"synthetic://rovereto_digital_library/{item_uuid}",
        "@type": "sc:Manifest",
        "label": title,
        "metadata": [
            {"label": "Portale", "value": "Rovereto Digital Library"},
            {"label": "Item API", "value": item_api_url},
        ],
        "seeAlso": [{"@id": source_pdf_url, "format": "application/pdf"}] if source_pdf_url else [],
        "sequences": [
            {
                "@id": f"synthetic://rovereto_digital_library/{item_uuid}/sequence/1",
                "@type": "sc:Sequence",
                "canvases": canvases,
            }
        ],
    }


def _build_memooria_manifest(page_url: str) -> str | None:
    """Memooria/Jarvis (qualsiasi biblioteca):
    - URL legacy:  .../schedadl.aspx?id={guid}
    - URL nuovo COOSMO: .../catalog/{collUuid}/cultural-item/{guid}
    → https://{subdomain}.jarvis.memooria.org/meta/iiif/{guid}/manifest (IIIF v2/v3)
    """
    # Estrae il hostname (es. brixiana.jarvis.memooria.org, parma.jarvis.memooria.org)
    host_m = re.search(r'https?://([^/]+\.jarvis\.memooria\.org)', page_url, re.IGNORECASE)
    _guid_pat = r'([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})'
    # Formato COOSMO nuovo: /cultural-item/{guid}
    coosmo_m = re.search(r'/cultural-item/' + _guid_pat, page_url, re.IGNORECASE)
    # Formato legacy Jarvis: ?id={guid}
    legacy_m = re.search(r'[?&]id=' + _guid_pat, page_url, re.IGNORECASE)
    guid_m = coosmo_m or legacy_m
    if host_m and guid_m:
        host = host_m.group(1).lower()
        guid = guid_m.group(1).lower()
        return f"https://{host}/meta/iiif/{guid}/manifest"
    # Fallback: nessun hostname esplicito ma GUID presente
    if guid_m:
        guid = guid_m.group(1).lower()
        return f"https://brixiana.jarvis.memooria.org/meta/iiif/{guid}/manifest"
    return None

# Alias per compatibilità con portale "brixiana" già configurato
_build_brixiana_manifest = _build_memooria_manifest


def _build_bncf_teca_manifest(page_url: str) -> str | list | None:
    """BNCF Teca (Firenze):
    ?idr=BNCF00004140909 → prova standard e manuscript
    """
    m = re.search(r'[?&]idr=([A-Za-z0-9]+)', page_url)
    if m:
        idr = m.group(1)
        # Restituiamo una lista di tentativi (URL)
        return [
            f"https://teca.bncf.firenze.sbn.it/iiif/manuscript/{idr}/manifest.json",
            f"https://teca.bncf.firenze.sbn.it/iiif/2/manifest/{idr}?format=json"
        ]
    return None


def build_bncf_teca_synthetic_manifest(page_url: str, working_folder: str) -> dict | None:
    """
    Crea un manifest sintetico per BNCF Teca quando il manifest IIIF standard fallisce.
    Interroga la servlet readBook per ottenere l'elenco delle immagini.
    """
    import os
    import re
    import requests
    import traceback

    logger.debug(
        "[BNCF Synthetic] build_bncf_teca_synthetic_manifest: "
        f"page_url={page_url}, working_folder={working_folder}"
    )
    m = re.search(r'[?&]idr=([A-Za-z0-9]+)', page_url)
    if not m:
        logger.error(f"[BNCF Synthetic] Impossibile estrarre idr da page_url: {page_url}")
        return None
    work_idr = m.group(1)

    xml_url = f"https://teca.bncf.firenze.sbn.it/ImageViewer/servlet/ImageViewer?idr={work_idr}&azione=readBook"
    logger.debug(f"[BNCF Synthetic] xml_url={xml_url}")
    try:
        h = {"User-Agent": "Mozilla/5.0"}
        r = requests.get(xml_url, headers=h, timeout=15)
        if not r.ok:
            logger.error(f"[BNCF Synthetic] Errore HTTP {r.status_code} su {xml_url}")
            return None

        logger.debug(f"[BNCF Synthetic] XML ricevuto ({len(r.text)} byte).")
        if os.environ.get("ATKPRO_BNCF_DEBUG_XML") == "1" and working_folder:
            try:
                os.makedirs(working_folder, exist_ok=True)
                xml_debug_path = os.path.join(working_folder, "bncf_xml_debug.xml")
                with open(xml_debug_path, "w", encoding="utf-8") as fxml:
                    fxml.write(r.text)
                logger.debug(f"[BNCF Synthetic] XML salvato per debug: {xml_debug_path}")
            except Exception as e2:
                logger.error(f"[BNCF Synthetic] Errore salvataggio XML: {e2}\n{traceback.format_exc()}")

        matches = re.findall(r'ID="([^"]+)"[^>]+?sequenza="([^"]+)"', r.text, re.DOTALL)
        logger.debug(f"[BNCF Synthetic] Numero match trovati: {len(matches)}")

        images = []
        for img_id, seq in matches:
            images.append((img_id, seq))

        logger.info(f"[BNCF Synthetic] Trovate {len(images)} immagini tramite Regex ultra-permissiva")

        if not images:
            # Tentativo disperato: cerca solo gli ID se sequenza fallisce
            ids = re.findall(r'ID="(BNCF[0-9]+)"', r.text)
            if ids:
                logger.warning(f"[BNCF Synthetic] Trovati {len(ids)} ID senza sequenza esplicita, genero sequenza numerica")
                images = [(id_val, str(i+1)) for i, id_val in enumerate(ids)]

        if not images:
            logger.error("[BNCF Synthetic] Nessuna immagine trovata nell'XML con nessun metodo.")
            return None

        # Costruisci manifest sintetico
        manifest = {
            "@context": "http://iiif.io/api/presentation/2/context.json",
            "@id": f"synthetic-bncf-{work_idr}",
            "@type": "sc:Manifest",
            "label": f"BNCF Teca - {work_idr} (Synthetic)",
            "sequences": [{
                "@type": "sc:Sequence",
                "canvases": []
            }]
        }

        for img_id, seq in images:
            # URL immagine (alta risoluzione tramite servlet showImg)
            img_url = f"https://teca.bncf.firenze.sbn.it/ImageViewer/servlet/ImageViewer?idr={img_id}&azione=showImg&sequence={seq}&reduce=0"

            canvas = {
                "@id": f"canvas-{img_id}",
                "@type": "sc:Canvas",
                "label": f"Pagina {seq}",
                "width": 2000, "height": 3000,
                "images": [{
                    "@type": "oa:Annotation",
                    "motivation": "sc:painting",
                    "resource": {
                        "@id": img_url,
                        "@type": "dctypes:Image",
                        "format": "image/jpeg",
                        "service": {
                            "@context": "http://iiif.io/api/image/2/context.json",
                            "@id": img_url,
                            "profile": "http://iiif.io/api/image/2/level0.json"
                        }
                    },
                    "on": f"canvas-{img_id}"
                }]
            }
            manifest["sequences"][0]["canvases"].append(canvas)

        return manifest
    except Exception as e:
        import logging, traceback
        logging.error(f"[BNCF Synthetic] Errore: {e}\n{traceback.format_exc()}")
        return None


def _build_findbuch_manifest(page_url: str) -> str | None:
    """findbuch.net: *.findbuch.net/php/view.php?link={hex}
    Supporta: kirchenbücher-südtirol.findbuch.net e tutti i subdomain findbuch.net
    Restituisce l'URL della pagina come placeholder (elaborato da build_findbuch_synthetic_manifest).
    """
    if re.search(r'findbuch\.net/php/view\.php', page_url, re.IGNORECASE):
        return page_url
    return None


def build_findbuch_synthetic_manifest(page_url: str) -> dict | None:
    """
    Costruisce un manifest IIIF sintetico per un registro findbuch.net.
    Scarica l'HTML del viewer e ne estrae be_id, ve_id e il numero di immagini.
    Il download avviene via gtpc.php con una sessione PHP attivata da main.php+view.php.
    """
    # Ricava base URL (es. https://www.kirchenbücher-südtirol.findbuch.net/php/)
    from urllib.parse import urlparse
    parsed = urlparse(page_url)
    base_url = f"{parsed.scheme}://{parsed.netloc}/php/"

    try:
        _h = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:136.0) Gecko/20100101 Firefox/136.0',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        }
        # Attiva la sessione PHP visitando main.php prima di view.php
        _sess = requests.Session()
        _sess.get(base_url + 'main.php', headers=_h, timeout=15)
        r = _sess.get(page_url, headers={**_h, 'Referer': base_url + 'main.php'}, timeout=20)
        r.raise_for_status()
        r.encoding = 'utf-8'
        html = r.text
    except Exception as e:
        logger.error(f"[Findbuch] Errore fetch pagina {page_url}: {e}")
        return None

    # Estrai be_id e ve_id dal JS inline della pagina viewer
    be_id_m  = re.search(r'var\s+be_id\s*=\s*(\d+)', html)
    ve_id_m  = re.search(r"var\s+ve_id\s*=\s*['\"]?(\d+)['\"]?", html)
    max_m    = re.search(r'var\s+max\s*=\s*(\d+)', html)
    if not be_id_m or not ve_id_m:
        logger.error(f"[Findbuch] be_id/ve_id non trovati in {page_url}")
        return None

    be_id  = int(be_id_m.group(1))
    ve_id  = int(ve_id_m.group(1))
    n_imgs = int(max_m.group(1)) if max_m else 0

    # Estrai pic_names per le label (opzionale, fallback a "Pagina N")
    pic_names = re.findall(r"pic_names\[\d+\]\s*=\s*'([^']+)'", html)

    if n_imgs == 0:
        logger.error(f"[Findbuch] max=0 immagini in {page_url}")
        return None

    # Estrai titolo dall'HTML
    bestand_m = re.search(r'<b>Bestand:</b></div>\s*<div[^>]*>([^<]+)</div>', html)
    titel_m   = re.search(r'<b>Titel:</b></div>\s*<div[^>]*>([^<]+)</div>', html)
    if titel_m and bestand_m:
        title = f"{bestand_m.group(1).strip()} – {titel_m.group(1).strip()}"
    elif bestand_m:
        title = bestand_m.group(1).strip()
    elif titel_m:
        title = titel_m.group(1).strip()
    else:
        title = "Registro findbuch"

    link_m = re.search(r'[?&]link=([A-Za-z0-9]+)', page_url)
    link_id = link_m.group(1) if link_m else "unknown"

    def _make_canvas(idx: int) -> dict:
        label = pic_names[idx] if idx < len(pic_names) else f"Pagina {idx + 1}"
        return {
            '@id': f"synthetic://findbuch/{link_id}/canvas/{idx}",
            '@type': 'sc:Canvas',
            'label': label,
            'width': 1000,
            'height': 1400,
            'images': [{
                '@type': 'oa:Annotation',
                'motivation': 'sc:painting',
                'resource': {
                    '@type': 'dctypes:Image',
                    '@id': f"gtpc://findbuch/{be_id}/{ve_id}/{idx}",
                    'format': 'image/jpeg',
                    'service': {
                        '@context': 'findbuch_gtpc',
                        '@id': f"gtpc://findbuch/{be_id}/{ve_id}/{idx}",
                        'be_id': be_id,
                        've_id': ve_id,
                        'count': idx,
                        'view_url': page_url,
                        'base_url': base_url,
                    }
                }
            }]
        }

    canvases = [_make_canvas(i) for i in range(n_imgs)]
    logger.info(f"[Findbuch] Manifest sintetico: '{title}', {n_imgs} immagini (be_id={be_id}, ve_id={ve_id})")

    return {
        '@context': 'http://iiif.io/api/presentation/2/context.json',
        '@id': f"synthetic://findbuch/{link_id}",
        '@type': 'sc:Manifest',
        'label': title,
        'sequences': [{
            '@id': f"synthetic://findbuch/{link_id}/sequence/1",
            '@type': 'sc:Sequence',
            'canvases': canvases
        }]
    }


def _build_matricula_manifest(page_url: str) -> str | None:
    """Matricula Online: https://data.matricula-online.eu/de/{nazione}/{diocesi}/{parrocchia}/{libro}/
    Restituisce l'URL della pagina come placeholder (elaborato da build_matricula_synthetic_manifest).
    """
    if re.search(r'data\.matricula-online\.eu/', page_url, re.IGNORECASE):
        return page_url
    return None


def _build_bnc_roma_manifest(page_url: str) -> str | None:
    """BNC Roma (digitale.bnc.roma.sbn.it): URL item-level gestito via manifest sintetico."""
    if re.search(
        r'digitale\.bnc\.roma\.sbn\.it/(printedbooks|publicisticmaterial|maps|picturematerial)/',
        page_url,
        re.IGNORECASE,
    ):
        return page_url
    return None


def _build_museogalileo_manifest(page_url: str) -> str | None:
    """Museogalileo Digiteca: URL viewer/opera gestito via manifest sintetico."""
    if re.search(r'bibdig\.museogalileo\.it/(?:Teca/Viewer\?an=|tecanew/opera\?bid=|TecaService/Teca/Opera\?bid=)', page_url, re.IGNORECASE):
        return page_url
    return None


def _extract_internetculturale_params(page_url: str) -> tuple[str | None, str | None]:
    """Estrae oai-id e teca da URL Internet Culturale (viewresource/iccu.jsp/magparser)."""
    try:
        p = urlparse(page_url)
        q = parse_qs(p.query or "")
    except Exception:
        return None, None

    raw_id = (q.get('id') or [None])[0]
    raw_teca = (q.get('teca') or q.get('descSourceLevel2') or [None])[0]

    oai_id = unquote_plus(raw_id).strip() if raw_id else None
    teca = unquote_plus(raw_teca).strip() if raw_teca else None

    if oai_id and not oai_id.lower().startswith('oai:'):
        oai_id = None

    if not teca:
        teca = 'MagTeca - ICCU'

    return oai_id, teca


def _build_internetculturale_estense_manifest(page_url: str) -> str | None:
    """Internet Culturale (Estense): URL item-level gestito via manifest sintetico."""
    if not re.search(r'internetculturale\.it', page_url, re.IGNORECASE):
        return None

    # Supporta i percorsi tipici: viewresource, iccu.jsp e magparser.
    if not re.search(r'/(?:it/16/search/viewresource|jmms/iccuviewer/iccu\.jsp|jmms/magparser)', page_url, re.IGNORECASE):
        return None

    oai_id, _teca = _extract_internetculturale_params(page_url)
    if oai_id:
        return page_url
    return None


def _fetch_internetculturale_mag(oai_id: str, teca_candidates: list[str], timeout: int = 35) -> tuple[str | None, str | None, str | None]:
    """Fetch robusto MAG parser con retry su errori transitori e fallback teca."""
    _h = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    transient = {408, 429, 500, 502, 503, 504}
    last_err = None

    for teca in teca_candidates:
        mag_url = (
            "https://www.internetculturale.it/jmms/magparser"
            f"?id={quote_plus(oai_id)}&teca={quote_plus(teca)}&mode=all&fulltext=0"
        )
        for attempt in range(1, 4):
            try:
                r = requests.get(mag_url, headers=_h, timeout=timeout)
                if r.ok:
                    txt = r.text
                    # Considera valido solo se contiene pagine o src immagini cacheman.
                    if '<page' in txt.lower() or 'cacheman/normal/' in txt.lower():
                        return txt, teca, mag_url
                    last_err = f"payload senza pagine per teca='{teca}'"
                    break
                last_err = f"HTTP {r.status_code} su teca='{teca}'"
                if r.status_code in transient and attempt < 3:
                    time.sleep(0.7 * attempt)
                    continue
                break
            except Exception as e:
                last_err = f"errore rete teca='{teca}': {e}"
                if attempt < 3:
                    time.sleep(0.7 * attempt)
                    continue
                break

    return None, None, last_err


def build_internetculturale_estense_synthetic_manifest(page_url: str) -> dict | None:
    """
    Costruisce un manifest IIIF sintetico da Internet Culturale / MagTeca.
    Flusso:
    - estrae id OAI e teca da URL item-level
    - chiama /jmms/magparser?id=<oai>&teca=<teca>&mode=all&fulltext=0
    - converte i tag <page ... src="cacheman/normal/..."> in canvases diretti JPEG
    """
    oai_id, teca = _extract_internetculturale_params(page_url)
    if not oai_id:
        logger.error(f"[InternetCulturale] Impossibile estrarre OAI id da {page_url}")
        return None

    teca_candidates = []
    if teca:
        teca_candidates.append(teca)
    if 'MagTeca - ICCU' not in teca_candidates:
        teca_candidates.append('MagTeca - ICCU')

    txt, teca_used, mag_url = _fetch_internetculturale_mag(oai_id, teca_candidates, timeout=35)
    if not txt:
        logger.error(f"[InternetCulturale] Errore fetch magparser per {oai_id}: {mag_url or 'n/a'}")
        return None

    teca = teca_used or teca or 'MagTeca - ICCU'

    title_m = re.search(r'<title>([^<]+)</title>', txt, re.IGNORECASE)
    title = title_m.group(1).strip() if title_m else oai_id

    page_matches = list(re.finditer(r'<page\b([^>]+)>', txt, flags=re.IGNORECASE))
    if not page_matches:
        logger.error(f"[InternetCulturale] Nessun <page> trovato per {oai_id}")
        return None

    def _attr(attrs: str, name: str) -> str | None:
        m = re.search(rf'{name}="([^"]+)"', attrs, re.IGNORECASE)
        return m.group(1) if m else None

    canvases = []
    for idx, pm in enumerate(page_matches, start=1):
        attrs = pm.group(1)
        src = _attr(attrs, 'src')
        if not src:
            continue
        if src.startswith('http://') or src.startswith('https://'):
            img_url = src
        else:
            img_url = f"https://www.internetculturale.it/jmms/{src.lstrip('/')}"

        label = _attr(attrs, 'name') or f"Pagina {idx}"
        w = int(_attr(attrs, 'w') or 1000)
        h = int(_attr(attrs, 'h') or 1400)

        canvases.append({
            '@id': f"synthetic://internetculturale_estense/{oai_id}/canvas/{idx}",
            '@type': 'sc:Canvas',
            'label': label,
            'width': w,
            'height': h,
            'images': [{
                '@type': 'oa:Annotation',
                'motivation': 'sc:painting',
                'resource': {
                    '@type': 'dctypes:Image',
                    '@id': img_url,
                    'format': 'image/jpeg',
                    'service': {
                        '@context': 'internetculturale_cacheman_direct',
                        '@id': img_url,
                        'profile': 'internetculturale_cacheman_direct',
                        'oai_id': oai_id,
                        'teca': teca,
                    }
                }
            }]
        })

    if not canvases:
        logger.error(f"[InternetCulturale] Nessun canvas valido da magparser per {oai_id}")
        return None

    safe_id = re.sub(r'[^A-Za-z0-9._-]+', '_', oai_id)
    logger.info(f"[InternetCulturale] Manifest sintetico: '{title}', {len(canvases)} immagini (teca={teca})")
    return {
        '@context': 'http://iiif.io/api/presentation/2/context.json',
        '@id': f"synthetic://internetculturale_estense/{safe_id}",
        '@type': 'sc:Manifest',
        'label': title,
        'sequences': [{
            '@id': f"synthetic://internetculturale_estense/{safe_id}/sequence/1",
            '@type': 'sc:Sequence',
            'canvases': canvases,
        }],
    }


def build_museogalileo_synthetic_manifest(page_url: str) -> dict | None:
    """
    Costruisce un manifest IIIF sintetico da endpoint Museogalileo TecaService.
    Flusso:
    - estrae bid/an dall'URL
    - chiama TecaService/Teca/Opera?bid=...
    - per ogni unit crea un canvas usando GetObject?id=<formato>&token=<token>
    """
    bid = None
    m = re.search(r'[?&]bid=(\d+)', page_url, re.IGNORECASE)
    if m:
        bid = m.group(1)
    if not bid:
        m = re.search(r'[?&]an=(\d+)', page_url, re.IGNORECASE)
        if m:
            bid = m.group(1)
    if not bid:
        logger.error(f"[Museogalileo] Impossibile estrarre BID/AN da {page_url}")
        return None

    opera_url = f"https://bibdig.museogalileo.it/TecaService/Teca/Opera?bid={bid}"
    try:
        _h = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        r = requests.get(opera_url, headers=_h, timeout=25)
        r.raise_for_status()
        data = r.json()
    except Exception as e:
        logger.error(f"[Museogalileo] Errore fetch Opera {opera_url}: {e}")
        return None

    richiesta = data.get('richiesta', {}) if isinstance(data, dict) else {}
    opera = data.get('opera', {}) if isinstance(data, dict) else {}
    token = richiesta.get('token')
    bid_eff = richiesta.get('bidEffettivo') or opera.get('bid') or str(bid)
    title = (opera.get('titolo') or f"Opera Museogalileo {bid_eff}").strip()
    units = opera.get('units') or []

    if not token or not isinstance(units, list) or len(units) == 0:
        logger.error(f"[Museogalileo] Dati Opera incompleti per bid={bid}: token={bool(token)} units={len(units) if isinstance(units, list) else 0}")
        return None

    canvases = []
    for idx, u in enumerate(units, start=1):
        formati = u.get('formati') or []
        if not formati:
            continue
        preferred_high = next((f for f in formati if str(f.get('tipoFormato', '')).upper() == 'IMAGE_HIGH'), None)
        preferred_low = next((f for f in formati if str(f.get('tipoFormato', '')).upper() == 'IMAGE_LOW'), None)
        fmt = preferred_high or preferred_low or formati[0]
        fmt_id = fmt.get('id')
        if not fmt_id:
            continue

        img_url = f"https://bibdig.museogalileo.it/TecaService/Teca/GetObject?id={fmt_id}&token={token}"
        label = (u.get('titolo') or u.get('numerazione') or f"Pagina {idx}").strip()
        canvases.append({
            '@id': f"synthetic://museogalileo/{bid_eff}/canvas/{idx}",
            '@type': 'sc:Canvas',
            'label': label,
            'width': 1000,
            'height': 1400,
            'images': [{
                '@type': 'oa:Annotation',
                'motivation': 'sc:painting',
                'resource': {
                    '@type': 'dctypes:Image',
                    '@id': img_url,
                    'format': 'image/jpeg',
                    'service': {
                        '@context': 'museogalileo_teca_direct',
                        '@id': img_url,
                        'profile': 'museogalileo_teca_direct',
                        'bid': str(bid_eff),
                        'fmt_id': str(fmt_id),
                    }
                }
            }]
        })

    if not canvases:
        logger.error(f"[Museogalileo] Nessun canvas generato per bid={bid_eff}")
        return None

    logger.info(f"[Museogalileo] Manifest sintetico: '{title}', {len(canvases)} immagini")
    return {
        '@context': 'http://iiif.io/api/presentation/2/context.json',
        '@id': f"synthetic://museogalileo/{bid_eff}",
        '@type': 'sc:Manifest',
        'label': title,
        'sequences': [{
            '@id': f"synthetic://museogalileo/{bid_eff}/sequence/1",
            '@type': 'sc:Sequence',
            'canvases': canvases,
        }],
    }


def build_bnc_roma_synthetic_manifest(page_url: str, html: str | None = None) -> dict | None:
    """
    Costruisce un manifest IIIF sintetico per BNC Roma a partire dalla pagina item-level.
    Estrae i path immagine /img/.../(thumbCrop|med), normalizza a /med e crea i canvas.
    """
    if html is None:
        try:
            _h = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
            r = requests.get(page_url, headers=_h, timeout=20)
            r.raise_for_status()
            r.encoding = 'utf-8'
            html = r.text
        except Exception as e:
            logger.error(f"[BNC] Errore fetch pagina {page_url}: {e}")
            return None

    img_matches = re.findall(
        r'(?:https?://digitale\.bnc\.roma\.sbn\.it)?(/img/(?:printedbooks|publicisticmaterial|maps|picturematerial)/[^"\'\s<>]+/(?:thumbCrop|med))',
        html,
        flags=re.IGNORECASE,
    )
    if not img_matches:
        logger.error(f"[BNC] Nessun path immagine trovato in {page_url}")
        return None

    # Normalizza tutti i path a immagini medie (/med), poi deduplica preservando ordine
    normalized = []
    seen = set()
    for p in img_matches:
        p_med = re.sub(r'/(thumbCrop|med)$', '/med', p, flags=re.IGNORECASE)
        abs_url = f"http://digitale.bnc.roma.sbn.it{p_med}"
        if abs_url not in seen:
            seen.add(abs_url)
            normalized.append(abs_url)

    if not normalized:
        logger.error(f"[BNC] Nessuna URL immagine normalizzata in {page_url}")
        return None

    # Prova ordinamento per numero pagina finale (_NNN/med), fallback ordine di estrazione
    def _page_num(u: str):
        m = re.search(r'_(\d{1,4})/med$', u)
        return int(m.group(1)) if m else None

    if all(_page_num(u) is not None for u in normalized):
        normalized.sort(key=lambda u: _page_num(u))

    title_m = re.search(r'<title>([^<]+)</title>', html, re.IGNORECASE)
    title = title_m.group(1).strip() if title_m else "Documento BNC Roma"

    bnc_id = re.sub(r'^https?://digitale\.bnc\.roma\.sbn\.it/', '', page_url.strip('/'), flags=re.IGNORECASE)
    bnc_id = re.sub(r'[^A-Za-z0-9_\-/]', '_', bnc_id)

    def _make_canvas(idx: int, img_url: str) -> dict:
        return {
            '@id': f"synthetic://bnc_roma/{bnc_id}/canvas/{idx+1}",
            '@type': 'sc:Canvas',
            'label': f"Pagina {idx+1}",
            'width': 1000,
            'height': 1400,
            'images': [{
                '@type': 'oa:Annotation',
                'motivation': 'sc:painting',
                'resource': {
                    '@type': 'dctypes:Image',
                    '@id': img_url,
                    'format': 'image/jpeg',
                    'service': {
                        '@context': 'bnc_direct',
                        '@id': img_url,
                        'profile': 'bnc_direct',
                    },
                },
            }],
        }

    canvases = [_make_canvas(i, u) for i, u in enumerate(normalized)]
    logger.info(f"[BNC] Manifest sintetico: '{title}', {len(canvases)} immagini")

    return {
        '@context': 'http://iiif.io/api/presentation/2/context.json',
        '@id': f"synthetic://bnc_roma/{bnc_id}",
        '@type': 'sc:Manifest',
        'label': title,
        'sequences': [{
            '@id': f"synthetic://bnc_roma/{bnc_id}/sequence/1",
            '@type': 'sc:Sequence',
            'canvases': canvases,
        }],
    }


def build_matricula_synthetic_manifest(page_url: str, html: str | None = None) -> dict | None:
    """
    Costruisce un manifest IIIF sintetico per un registro Matricula Online.
    Estrae i /image/base64url dal viewer JS MatriculaDocView, decodifica ogni
    URL JPEG e costruisce il manifest.

    Se html è fornito (es. già ottenuto via Selenium), viene usato direttamente
    senza un secondo fetch HTTP (che fallirebbe con 503 bot-blocker).
    Le immagini usano service['@context'] = 'matricula_direct' per essere
    riconosciute da elaborazione.py (nessun header speciale richiesto).
    """
    import base64 as _b64
    if html is None:
        try:
            _h = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
            r = requests.get(page_url, headers=_h, timeout=20)
            r.raise_for_status()
            r.encoding = 'utf-8'
            html = r.text
        except Exception as e:
            logger.error(f"[Matricula] Errore fetch pagina {page_url}: {e}")
            return None

    # Estrai URL immagini codificate base64 dal viewer MatriculaDocView
    encoded_imgs = re.findall(r'"/image/([A-Za-z0-9+/=]{20,})"', html)
    if not encoded_imgs:
        logger.error(f"[Matricula] Nessuna immagine trovata in {page_url}")
        return None

    # Decodifica ogni URL base64 → URL JPEG su hosted-images.matricula-online.eu
    img_urls = []
    for enc in encoded_imgs:
        try:
            padded = enc + '=' * (-len(enc) % 4)
            decoded = re.sub(r'[\x00-\x1f\x7f]', '', _b64.b64decode(padded).decode('utf-8')).rstrip('/?')
            decoded = decoded.replace('http://', 'https://', 1)  # forza HTTPS
            img_urls.append(decoded)
        except Exception:
            continue

    if not img_urls:
        logger.error(f"[Matricula] Nessuna URL decodificabile in {page_url}")
        return None

    # Etichette pagina dall'array "labels"
    labels_m = re.search(r'"labels":\s*\[([^\]]+)\]', html)
    if labels_m:
        labels = re.findall(r'"([^"]+)"', labels_m.group(1))
    else:
        labels = [f"Pagina {i + 1}" for i in range(len(img_urls))]

    # Titolo dal <title>: "Taufbuch - 01-001 | Parrocchia | Diocesi | Matricula Online"
    title_m = re.search(r'<title>([^<]+)</title>', html)
    title = title_m.group(1).strip() if title_m else "Registro Matricula"
    if ' | Matricula' in title:
        title = title[:title.index(' | Matricula')]

    # ID univoco dall'URL (es. "oesterreich/wien/01-st-stephan/01-001")
    mat_id = re.sub(r'https?://data\.matricula-online\.eu/[a-z]{2}/', '', page_url).strip('/')

    def _make_canvas(idx: int, img_url: str, label: str) -> dict:
        return {
            '@id': f"synthetic://matricula/{mat_id}/canvas/{idx}",
            '@type': 'sc:Canvas',
            'label': label,
            'width': 1000,
            'height': 1400,
            'images': [{
                '@type': 'oa:Annotation',
                'motivation': 'sc:painting',
                'resource': {
                    '@type': 'dctypes:Image',
                    '@id': img_url,
                    'format': 'image/jpeg',
                    'service': {
                        '@context': 'matricula_direct',
                        '@id': img_url,
                        'profile': 'matricula_direct'
                    }
                }
            }]
        }

    canvases = [
        _make_canvas(i, u, labels[i] if i < len(labels) else f"Pagina {i + 1}")
        for i, u in enumerate(img_urls)
    ]
    logger.info(f"[Matricula] Manifest sintetico: '{title}', {len(img_urls)} immagini")

    return {
        '@context': 'http://iiif.io/api/presentation/2/context.json',
        '@id': f"synthetic://matricula/{mat_id}",
        '@type': 'sc:Manifest',
        'label': title,
        'sequences': [{
            '@id': f"synthetic://matricula/{mat_id}/sequence/1",
            '@type': 'sc:Sequence',
            'canvases': canvases
        }]
    }


# Mappa portale → funzione builder
_STANDARD_IIIF_BUILDERS = {
    "gallica": _build_gallica_manifest,
    "vatlib": _build_vatlib_manifest,
    "bodleian": _build_bodleian_manifest,
    "europeana": _build_europeana_manifest,
    "internet_archive": _build_ia_manifest,
    "e_rara": _build_e_rara_manifest,
    "e_codices": _build_ecodices_manifest,
    "e_manuscripta": _build_e_manuscripta_manifest,
    "heidelberg": _build_heidelberg_manifest,
}

_ITALIAN_LIBRARY_BUILDERS = {
    "biblioteca_digitale_siena": _build_biblioteca_digitale_siena_manifest,
    "bub_digitale": _build_bub_digitale_manifest,
    "dl_ficlit": _build_dl_ficlit_manifest,
    "biblioteca_digitale_trentina": _build_biblioteca_digitale_trentina_manifest,
    "biblioteca_digitale_lombarda": _build_biblioteca_digitale_lombarda_manifest,
    "rovereto_digital_library": _build_rovereto_manifest,
    "museogalileo": _build_museogalileo_manifest,
    "internetculturale_estense": _build_internetculturale_estense_manifest,
    "bnc_roma": _build_bnc_roma_manifest,
    "bncf_teca": _build_bncf_teca_manifest,
}

_SPECIAL_COLLECTION_BUILDERS = {
    "brixiana": _build_memooria_manifest,
    "memooria": _build_memooria_manifest,
    "findbuch": _build_findbuch_manifest,
    "matricula": _build_matricula_manifest,
}

_PORTAL_BUILDERS = {
    **_STANDARD_IIIF_BUILDERS,
    **_ITALIAN_LIBRARY_BUILDERS,
    **_SPECIAL_COLLECTION_BUILDERS,
}


def _normalize_manifest_portal_key(portale: str) -> str:
    return portale.lower().replace("-", "_").replace(" ", "_")


def _get_manifest_builder(portale: str):
    portale_key = _normalize_manifest_portal_key(portale)
    return portale_key, _PORTAL_BUILDERS.get(portale_key)


def resolve_manifest_url(page_url: str, portale: str) -> str | dict | None:
    """
    Costruisce l'URL del manifest IIIF o restituisce un dict (manifest sintetico)
    partendo dall'URL di pagina.
    """
    portale_key, builder = _get_manifest_builder(portale)
    if portale_key == "manifest_diretto":
        return page_url

    if portale_key == "bncf_teca":
        # Prima proviamo IIIF standard (tentativi multipli)
        urls = _build_bncf_teca_manifest(page_url)
        if urls:
            import requests
            for std_url in (urls if isinstance(urls, list) else [urls]):
                try:
                    r = requests.head(std_url, timeout=5, headers={"User-Agent": "Mozilla/5.0"})
                    if r.ok: return std_url
                except: pass
        # Fallback sintetico
        return build_bncf_teca_synthetic_manifest(page_url, "")

    if builder:
        return builder(page_url)
    return None

def find_manifest_url(driver) -> str | None:
    """
    Compatibilità v1.4.1: legge il DOM da Selenium e cerca containers/.../manifest.
    Riprende sleep e messaggi identici per allineare i log.
    """
    time.sleep(3)
    print("[Manifest] Cerco manifest nell'HTML...")
    try:
        html = driver.page_source
    except Exception as e:
        logger.warning(f"[Manifest] Impossibile leggere page_source: {e}")
        html = ""
    manifest_url = _find_manifest_in_html(html)
    if not manifest_url:
        print("[Manifest] Nessun manifest trovato nell'HTML.")
    return manifest_url

def robust_find_manifest(page_url: str, html: str | None = None) -> str | None:
    """
    Ricerca robusta del manifest quando si parte dall'URL della pagina.
    - Se viene passato html, prova subito il parsing v1.4.1.
    - Altrimenti scarica l'HTML con HEADERS_UX e cerca i link containers/.../manifest.
    - Prova anche varianti con slash finale.
    - Come ultimo tentativo, parse di script JSON/Mirador che contengono 'manifest'.
    """
    manifest_from_query = extract_manifest_url_from_viewer_url(page_url)
    if manifest_from_query:
        print(f"[Manifest] Trovato da query viewer: {manifest_from_query}")
        return manifest_from_query

    # 1) Se abbiamo già HTML, prova subito
    if html:
        print("[Manifest] Cerco nell'HTML...")
        m = _find_manifest_in_html(html)
        if m:
            return m
        print("[Manifest] Nessun manifest trovato nell'HTML.")

    # 2) Scarica l'HTML della pagina come browser reale (HEADERS_UX)
    print("[Manifest] Scarico HTML della pagina...")
    r = _http_get(page_url, timeout=25)
    if r and r.ok:
        text = r.text or ""
        # Parsing diretto (v1.4.1)
        print("[Manifest] Cerco nell'HTML...")
        m = _find_manifest_in_html(text)
        if m:
            return m

        # 3) Varianti con slash finale o link indiretti
        if page_url.endswith("/"):
            alt_url = page_url[:-1]
        else:
            alt_url = page_url + "/"
        if alt_url != page_url:
            print("[Manifest] Provo variante URL...")
            r2 = _http_get(alt_url, timeout=20)
            if r2 and r2.ok:
                m2 = _find_manifest_in_html(r2.text or "")
                if m2:
                    print("[Manifest] Trovato via slash finale.")
                    return m2

        # 4) Parsing di script Mirador/JSON inline (casi in cui 'manifest' appare in oggetti)
        print("[Manifest] Cerco in script/JSON inline...")
        # Cerca 'manifest' come chiave o valore di oggetti json embed
        m3 = re.search(
            r'"manifest"\s*:\s*"(https://dam-antenati\.cultura\.gov\.it/antenati/containers/[A-Za-z0-9]+/manifest(?:\.json)?)"',
            text
        )
        if m3:
            manifest_url = m3.group(1)
            print(f"[Manifest] Trovato: {manifest_url}")
            return manifest_url

    # 5) Nessun manifest trovato
    print("[Manifest] Nessun manifest trovato.")
    return None

def download_manifest(manifest_url: str, output_folder: str, titolo_doc: str = "documento", referer: str | None = None) -> dict | None:
    """
    Scarica il manifest replicando la logica v1.4.1:
    - HEADERS_UX completi (User-Agent, Accept, Referer, Origin, Accept-Language, Connection)
    - Gestione esplicita di 403 e 5xx
    - Salvataggio su disco con nome identico alla v1.4.1
    - Messaggi di log identici per verifica bit-a-bit
    - referer: se fornito, sovrascrive Referer/Origin negli header (per portali non-Antenati)
    """
    print(f"[Manifest] Download da: {manifest_url}")
    # Adatta gli header al portale: usa referer specificato o default Antenati
    viewer_manifest_url = extract_manifest_url_from_viewer_url(manifest_url)
    if viewer_manifest_url:
        print(f"[Manifest] URL viewer ricevuto, uso manifestId: {viewer_manifest_url}")
        manifest_url = viewer_manifest_url

    headers = _manifest_headers(manifest_url, referer=referer)
    max_retries = 3
    delay = 1.0
    for attempt in range(1, max_retries + 1):
        try:
            response = requests.get(manifest_url, headers=headers, timeout=25)

            # Log codici utili
            if response is None:
                print(f"[Manifest] Tentativo {attempt}: Nessuna risposta")
            else:
                print(f"[Manifest] Tentativo {attempt}: codice {response.status_code}")

            if response is None:
                raise requests.exceptions.RequestException("Nessuna risposta")

            if response.status_code == 403:
                print("[Manifest] Accesso negato (403).")
                return None

            # In caso di errori server (5xx) proviamo un retry
            if response.status_code >= 500:
                print(f"[Manifest] Errore server ({response.status_code}) al tentativo {attempt}.")
                if attempt < max_retries:
                    time.sleep(delay)
                    delay *= 2
                    continue
                else:
                    return None

            response.raise_for_status()
            try:
                manifest = response.json()
            except Exception as e:
                try:
                    content = getattr(response, "content", b"")
                    if isinstance(content, (bytes, bytearray)):
                        content = content.decode("utf-8-sig")
                    if not isinstance(content, str):
                        raise TypeError("Contenuto risposta non testuale")
                    manifest = json.loads(content)
                except Exception:
                    response_text = getattr(response, "text", "")
                    if isinstance(response_text, (bytes, bytearray)):
                        response_text = response_text.decode("utf-8", errors="replace")
                    preview = response_text[:180].replace("\r", " ").replace("\n", " ") if isinstance(response_text, str) else ""
                    print(f"[Manifest] Contenuto manifest non decodificabile: {e}")
                    if preview:
                        print(f"[Manifest] Anteprima risposta non JSON: {preview}")
                    return None

            manifest = normalize_iiif_manifest_for_processing(manifest)

            os.makedirs(output_folder, exist_ok=True)

            # Estrai ID contenitore dall'URL (identico alla v1.4.1)
            container_id = manifest_url.strip("/").split("/")[-2]
            titolo_pulito = re.sub(r'[\\/*?:"<>|]', "", titolo_doc).replace(" ", "_")
            manifest_filename = f"manifest_{container_id}_{titolo_pulito}.json"
            manifest_path = os.path.join(output_folder, manifest_filename)

            with open(manifest_path, "w", encoding="utf-8") as f:
                json.dump(manifest, f, ensure_ascii=False, indent=2)

            print(f"[Manifest] Salvato in: {manifest_path}")
            return manifest

        except requests.exceptions.RequestException as e:
            print(f"[Manifest] Tentativo {attempt} fallito: {e}")
            if attempt < max_retries:
                time.sleep(delay)
                delay *= 2
                continue
            else:
                print(f"[Manifest] Errore download definitivo dopo {max_retries} tentativi")
                return None
