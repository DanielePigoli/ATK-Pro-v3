# -*- coding: utf-8 -*-
import os
import re
import json
import time
import logging
import concurrent.futures
import requests
from logging.handlers import RotatingFileHandler
import shutil
from PIL import Image

from manifest_utils import (
    download_manifest,
    extract_manifest_url_from_viewer_url,
    normalize_iiif_manifest_for_processing,
    robust_find_manifest,
)
try:
    from resource_profile import get_canvas_max_workers
except ImportError:
    from src.resource_profile import get_canvas_max_workers
try:
    from portal_registry import get_portal_referer, get_portal_tile_download_policy, normalize_portal_key
except ImportError:
    from src.portal_registry import get_portal_referer, get_portal_tile_download_policy, normalize_portal_key
from canvas_id_extractor import extract_canvas_id_from_url, extract_ud_canvas_id_from_infojson_xhr
from browser_setup import setup_selenium, setup_playwright
try:
    from src.user_prompts import ask_generate_pdf, ask_image_formats
except ImportError:
    from user_prompts import ask_generate_pdf, ask_image_formats
# ProgressDialog viene importato all'occorrenza per evitare problemi di circular import
from image_downloader import download_info_json
from tile_downloader import download_tiles
from tile_rebuilder import rebuild_image, build_image_metadata
from manifest_parser import estrai_metadati_da_manifest, build_manifest_url
from pdf_generator import create_pdf_from_images, enrich_pdf_metadata
from metadata_utils import embed_metadata_and_save, _save_sidecar_json_once
try:
    from atk_version import PACKAGE_VERSION as VERSION
except ImportError:
    from src.atk_version import PACKAGE_VERSION as VERSION



# --- Logging configurabile per ambiente ---
ATKPRO_ENV = os.environ.get("ATKPRO_ENV", "development").lower()
logger = logging.getLogger(__name__)
if not logger.hasHandlers():
    # Log su terminale sempre attivo
    handler = logging.StreamHandler()
    handler.setLevel(logging.DEBUG if ATKPRO_ENV != "production" else logging.WARNING)
    formatter = logging.Formatter('%(levelname)s: %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    # Log su file solo se non in produzione
    if ATKPRO_ENV != "production":
        file_handler = RotatingFileHandler('atkpro_output.log', maxBytes=5*1024*1024, backupCount=3, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter('%(asctime)s %(levelname)s: %(message)s')
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
logger.setLevel(logging.DEBUG if ATKPRO_ENV != "production" else logging.WARNING)

# State globale per GUI/main

def get_msg(glossario_data, chiave, lingua="IT"):
    """Restituisce un messaggio localizzato dal glossario.
    Supporta il formato JSON del glossario ({sezione: [{messaggio, IT, FR, ...}]}).
    Se non trovato, ritorna la chiave originale.
    """
    try:
        if glossario_data:
            lingua_up = lingua.upper() if lingua else "IT"
            if lingua_up == "DK":
                lingua_up = "DA"
            if lingua_up == "VN":
                lingua_up = "VI"
            for section in glossario_data.values():
                if isinstance(section, list):
                    for voce in section:
                        if voce.get("messaggio") == chiave:
                            return voce.get(lingua_up, voce.get("IT", None))
    except Exception:
        pass
    return chiave


def _parse_ua_from_url(url: str):
    """Estrae l'UA (Unità Archivistica) da un URL antenati."""
    m = re.search(r'/ark:/12657/(an_[u][ad]\d+)', url)
    if m:
        return m.group(1)
    return None


def _canvas_max_workers_for_portal(
    portale: str | None,
    cpu_count: int | None = None,
    resource_profile: str | None = None,
) -> int:
    """Restituisce il parallelismo canvas rispettando la policy prudenziale del portale."""
    portal_max_workers = None
    try:
        portal_max_workers, _ = get_portal_tile_download_policy(portale)
    except Exception:
        portal_max_workers = None

    try:
        return get_canvas_max_workers(
            resource_profile,
            cpu_count=cpu_count,
            portal_max_workers=portal_max_workers,
        )
    except Exception:
        return 4


def _ficlit_direct_image_url_from_canvas(canvas: dict) -> str | None:
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


def _download_direct_image(image_url: str, referer: str, timeout: int = 45):
    """Scarica una immagine diretta e restituisce una copia PIL."""
    from io import BytesIO

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Referer": referer,
    }
    response = requests.get(image_url, headers=headers, timeout=timeout)
    if not response.ok or not response.content:
        return None, response.status_code if response is not None else None, 0
    image = Image.open(BytesIO(response.content)).copy()
    return image, response.status_code, len(response.content)


def _parse_ark_from_url(url: str):
    """Estrae l'ARK completo da un URL antenati."""
    m = re.search(r'/ark:/12657/([^/#\s]+(?:/[^#\s]+)?)', url)
    if m:
        return "ark:/12657/" + m.group(1)
    return None


def _last_segment(s: str):
    """Estrae l'ultimo segmento di un percorso/URL."""
    if not s:
        return None
    s = s.rstrip('/').split('/')[-1]
    return s or None


def _museogalileo_extract_bid(url: str):
    """Estrae BID/AN da URL viewer/opera Museogalileo."""
    if not url:
        return None
    m = re.search(r'[?&]bid=(\d+)', url, re.IGNORECASE)
    if m:
        return m.group(1)
    m = re.search(r'[?&]an=(\d+)', url, re.IGNORECASE)
    if m:
        return m.group(1)
    return None


def _museogalileo_refresh_token(bid: str, timeout: int = 25):
    """Recupera token aggiornato da TecaService Opera."""
    if not bid:
        return None
    opera_url = f"https://bibdig.museogalileo.it/TecaService/Teca/Opera?bid={bid}"
    try:
        _h = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        r = requests.get(opera_url, headers=_h, timeout=timeout)
        r.raise_for_status()
        data = r.json() if r.content else {}
        richiesta = data.get('richiesta', {}) if isinstance(data, dict) else {}
        token = richiesta.get('token')
        return token if token else None
    except Exception as e:
        logger.warning(f"[Museogalileo] Refresh token fallito bid={bid}: {e}")
        return None


def _museogalileo_parse_getobject_url(img_url: str):
    """Estrae id/token da URL GetObject Museogalileo."""
    if not img_url:
        return None, None
    m_id = re.search(r'[?&]id=([^&]+)', img_url, re.IGNORECASE)
    m_tk = re.search(r'[?&]token=([^&]+)', img_url, re.IGNORECASE)
    fmt_id = m_id.group(1) if m_id else None
    token = m_tk.group(1) if m_tk else None
    return fmt_id, token


def _download_museogalileo_image(img_url: str, bid_hint: str = None, timeout: int = 45):
    """Download robusto immagine Museogalileo con retry e refresh token."""
    _h = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    current_url = img_url
    last_status = None
    retried_with_new_token = False

    for attempt in range(1, 4):
        try:
            r = requests.get(current_url, headers=_h, timeout=timeout)
            last_status = r.status_code
            if r.ok and len(r.content) > 0:
                return r.content, r.status_code, current_url

            # Token scaduto/non valido: prova refresh una sola volta.
            if r.status_code in (401, 403) and not retried_with_new_token:
                fmt_id, _old_token = _museogalileo_parse_getobject_url(current_url)
                bid = bid_hint
                if not bid:
                    bid = _museogalileo_extract_bid(current_url)
                new_token = _museogalileo_refresh_token(bid) if bid else None
                if new_token and fmt_id:
                    current_url = f"https://bibdig.museogalileo.it/TecaService/Teca/GetObject?id={fmt_id}&token={new_token}"
                    retried_with_new_token = True
                    logger.info(f"[Museogalileo] Token aggiornato per bid={bid}, nuovo tentativo download")
                    continue

            # Retry su errori transitori lato rete/server.
            if r.status_code in (408, 429, 500, 502, 503, 504) and attempt < 3:
                time.sleep(0.7 * attempt)
                continue

            return None, r.status_code, current_url
        except Exception as e:
            if attempt < 3:
                logger.warning(f"[Museogalileo] Tentativo {attempt}/3 fallito: {e}")
                time.sleep(0.7 * attempt)
                continue
            logger.error(f"[Museogalileo] Errore download definitivo: {e}")
            return None, last_status, current_url

    return None, last_status, current_url


def _normalize_format(fmt):
    """Normalizza il nome del formato (JPG->JPEG, TIF->TIFF)."""
    fmt_upper = fmt.upper().strip()
    if fmt_upper in ('JPG', 'JPEG'):
        return 'JPEG'
    elif fmt_upper in ('TIF', 'TIFF'):
        return 'TIFF'
    elif fmt_upper == 'PNG':
        return 'PNG'
    elif fmt_upper == 'PDF':
        return 'PDF'
    return fmt_upper


def _extract_pdf_url_from_entry(entry):
    """Estrae un URL PDF da voci IIIF seeAlso o da servizi sintetici."""
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


def _find_bdt_direct_pdf_url(tiles_info=None, manifest=None):
    """Trova il PDF diretto ufficiale nei manifest sintetici BDT, se presente."""
    return _find_direct_pdf_url(tiles_info, manifest, allowed_contexts={"bdt_direct"})


def _find_direct_pdf_url(tiles_info=None, manifest=None, allowed_contexts=None):
    """Trova un PDF diretto da seeAlso o da servizi sintetici espliciti."""
    if isinstance(manifest, dict):
        see_also_entries = manifest.get("seeAlso") or manifest.get("see_also") or []
        if isinstance(see_also_entries, dict):
            see_also_entries = [see_also_entries]
        for entry in see_also_entries:
            pdf_url = _extract_pdf_url_from_entry(entry)
            if pdf_url:
                return pdf_url

    for canvas in tiles_info or []:
        try:
            service = canvas.get("images", [{}])[0].get("resource", {}).get("service")
        except Exception:
            continue
        services = service if isinstance(service, list) else [service]
        for svc in services:
            if not isinstance(svc, dict):
                continue
            if allowed_contexts and svc.get("@context") not in allowed_contexts:
                continue
            pdf_url = svc.get("pdf_url") or _extract_pdf_url_from_entry(svc)
            if pdf_url:
                return str(pdf_url)
    return None


def save_image_variants(image: Image.Image, output_folder: str, base_filename: str, 
                       formats=['PNG', 'JPEG', 'TIFF'], meta: dict = None):
    """
    Salva immagine in più formati con metadati embed.
    Supporta PNG, JPEG (JPG), TIFF (TIF) con sidecar JSON.
    """
    os.makedirs(output_folder, exist_ok=True)
    
    # Normalizza i formati ricevuti (es. ['PNG', 'JPG', 'TIF'] -> ['PNG', 'JPEG', 'TIFF'])
    formats = [_normalize_format(f) for f in formats]
    
    logger.debug(f"[save_image_variants] image={image}, output={output_folder}, filename={base_filename}, formats={formats}")
    
    if image is None:
        logger.error("[Error] save_image_variants ricevuto image=None")
        return
    
    # Sidecar JSON (una sola volta) — usa helper centralizzato
    if meta and "_json" in meta:
        try:
            _save_sidecar_json_once(output_folder, base_filename, meta)
        except Exception as e:
            logger.warning(f"[Warning] Impossibile salvare sidecar JSON per {base_filename}: {e}")

    # --- LOGICA SUFFISSO UNIVOCO ---

    # --- LOGICA SUFFISSO UNIVOCO PER SESSIONE ---
    if not hasattr(save_image_variants, "_session_filenames") or save_image_variants._session_filenames is None:
        save_image_variants._session_filenames = {}
    session_filenames = save_image_variants._session_filenames
    key = os.path.abspath(output_folder)
    if key not in session_filenames:
        session_filenames[key] = set()

    def get_unique_filename_session(folder, filename, ext):
        used = session_filenames[os.path.abspath(folder)]
        candidate = filename
        i = 2
        while f"{candidate}.{ext}" in used:
            candidate = f"{filename}_rec{i}"
            i += 1
        used.add(f"{candidate}.{ext}")
        return candidate

    # PNG
    if 'PNG' in formats:
        unique_filename = get_unique_filename_session(output_folder, base_filename, "png")
        path = os.path.join(output_folder, f"{unique_filename}.png")
        try:
            try:
                embed_metadata_and_save(image, path, meta)
            except Exception:
                image.save(path, format='PNG')
            logger.info(f"[PNG] Salvata immagine: {path}")
        except Exception as e:
            logger.error(f"[Error] Errore salvataggio PNG {path}: {e}")

    # JPEG
    if 'JPEG' in formats:
        unique_filename = get_unique_filename_session(output_folder, base_filename, "jpg")
        path = os.path.join(output_folder, f"{unique_filename}.jpg")
        try:
            try:
                embed_metadata_and_save(image, path, meta)
            except Exception:
                img_rgb = image.convert("RGB") if image.mode != "RGB" else image
                img_rgb.save(path, format='JPEG', quality=95, progressive=True, optimize=True)
            logger.info(f"[JPEG] Salvata immagine: {path}")
        except Exception as e:
            logger.error(f"[Error] Errore salvataggio JPEG {path}: {e}")

    # TIFF
    if 'TIFF' in formats:
        path = os.path.join(output_folder, f"{base_filename}.tif")
        try:
            try:
                embed_metadata_and_save(image, path, meta)
            except Exception:
                image.save(path, format='TIFF', compression='tiff_lzw')
            logger.info(f"[TIFF] Salvata immagine: {path}")
        except Exception as e:
            logger.error(f"[Error] Errore salvataggio TIFF {path}: {e}")


def _save_direct_image_outputs(
    image: Image.Image,
    output_folder: str,
    base_filename: str,
    formats,
    meta: dict = None,
):
    """Salva una immagine diretta nei formati richiesti, incluso PDF se selezionato."""
    if not formats:
        formats = ['PNG', 'JPEG', 'TIFF']

    normalized_formats = [_normalize_format(fmt) for fmt in formats]
    image_formats = [fmt for fmt in formats if _normalize_format(fmt) != 'PDF']
    pdf_requested = 'PDF' in normalized_formats

    if image_formats:
        save_image_variants(image, output_folder, base_filename, image_formats, meta=meta)

    if pdf_requested:
        tmp_dir = os.path.join(output_folder, "_tmp_pdf_images")
        os.makedirs(tmp_dir, exist_ok=True)
        tmp_png = os.path.join(tmp_dir, f"{base_filename}_pdftmp.png")
        try:
            image.save(tmp_png, format='PNG')
            pdf_out = os.path.join(output_folder, f"{base_filename}.pdf")
            create_pdf_from_images(tmp_dir, pdf_out)
        finally:
            shutil.rmtree(tmp_dir, ignore_errors=True)


def _make_placeholder_image(service_id: str, width: int = 800, height: int = 1200,
                             glossario_data=None, lingua: str = "IT",
                             canvas_url: str = None) -> Image.Image:
    """Genera immagine placeholder per download falliti, da includere nel PDF."""
    from PIL import ImageDraw, ImageFont
    img = Image.new('RGB', (width, height), color=(240, 240, 240))
    draw = ImageDraw.Draw(img)
    font_large = font_medium = font_small = None
    for font_name in ("arial.ttf", "Arial.ttf", "DejaVuSans.ttf", "LiberationSans-Regular.ttf"):
        try:
            font_large = ImageFont.truetype(font_name, 36)
            font_medium = ImageFont.truetype(font_name, 24)
            font_small = ImageFont.truetype(font_name, 18)
            break
        except Exception:
            continue
    if font_large is None:
        font_large = font_medium = font_small = ImageFont.load_default()
    title = get_msg(glossario_data, "Download fallito", lingua) or "Download fallito"
    subtitle = get_msg(glossario_data, "Riprova usando il seguente link:", lingua) or "Riprova usando il seguente link:"
    draw.text((50, 80), title, fill=(200, 0, 0), font=font_large)
    draw.text((50, 160), subtitle, fill=(60, 60, 60), font=font_medium)
    url_to_show = canvas_url or service_id
    url_parts = [url_to_show[i:i+70] for i in range(0, len(url_to_show), 70)]
    y = 220
    for part in url_parts:
        draw.text((50, y), part, fill=(0, 0, 180), font=font_small)
        y += 28
    return img


class Elaborazione:
    def __init__(self, record_type: str, ark_url: str, output_dir: str, glossario_data=None, lingua="IT", portale: str = "antenati"):
        self.record_type = record_type.upper()
        self.ark_url = ark_url
        self.output_dir = output_dir
        self.nome_file = ""
        self.manifest = None
        self.manifest_path = None
        self.glossario_data = glossario_data
        self.lingua = lingua
        self.portale = portale

    def set_nome_file(self, nome: str):
        """Imposta il nome file per il record."""
        self.nome_file = nome

    def set_formats(self, formats):
        """Imposta i formati di output desiderati."""
        self.formats = formats
        return self

    def run(self, formats=None):
        """Orchestratore principale: scarica manifest e elabora record.
        Se formats è passato, lo usa; altrimenti usa self.formats."""
        if formats:
            self.formats = formats
        logger.info(f"[Elaborazione] Avvio run: output_dir={self.output_dir} nome_file={self.nome_file}")
        try:
            # Download manifest
            self.manifest = self._fetch_manifest()
            logger.info(f"[Elaborazione] Manifest scaricato: {self.manifest_path if self.manifest_path else 'N/A'}")
            if not self.manifest:
                logger.error("[Error] Manifest non disponibile")
                return False

            # Estrai canvas/tiles info
            tiles_info = self.manifest.get("sequences", [{}])[0].get("canvases", [])
            if not tiles_info:
                logger.error("[Error] Nessun canvas nel manifest")
                return False

            # Applica range canvas se specificato (1-based, inclusi)
            canvas_da = getattr(self, 'canvas_da', None)
            canvas_a = getattr(self, 'canvas_a', None)
            if canvas_da is not None or canvas_a is not None:
                _da = max(1, int(canvas_da or 1)) - 1  # converti in 0-based
                _a = int(canvas_a) if canvas_a is not None else len(tiles_info)
                tiles_info = tiles_info[_da:_a]
                logger.info(f"[Range] Canvas filtrati: {_da+1}-{_a} ({len(tiles_info)} totali)")

            metadata = self.manifest.get("metadata", {})

            # Processa in base al tipo
            if self.record_type == "D":
                logger.info(f"[Elaborazione] Tipo D: {self.nome_file}")
                return self._process_document(tiles_info, metadata)
            elif self.record_type == "R":
                logger.info(f"[Elaborazione] Tipo R: {self.nome_file}")
                return self._process_register(tiles_info, metadata)
            else:
                raise ValueError(f"Tipo record non riconosciuto: {self.record_type}")
        except Exception as e:
            logger.error(f"[Error] Errore elaborazione: {e}", exc_info=True)
            return False


    def _fetch_manifest(self):
        """Scarica il manifest IIIF."""
        try:
            # Logging diagnostico: mostra parametri chiave
            logger.info(f"[DEBUG] _fetch_manifest: self.ark_url={self.ark_url}")
            logger.info(f"[DEBUG] _fetch_manifest: self.portale={self.portale}")

            manifest_url = self._get_manifest_url()
            if not manifest_url:
                logger.error("[Error] Manifest URL non disponibile")
                return None

            # Crea sottocartella di lavoro univoca
            output_base = self.output_dir

            # Se manifest_url è un dict, usiamo un ID fittizio per la cartella o l'ID estratto dall'URL
            if isinstance(manifest_url, dict):
                container_id = re.search(r'idr=([A-Za-z0-9]+)', self.ark_url).group(1) if "idr=" in self.ark_url else "BNCF_SYNTH"
            else:
                container_id = manifest_url.strip("/").split("/")[-2]

            titolo_pulito = re.sub(r'[\\/*?:"<>|]', "", self.nome_file).replace(" ", "_")
            base_folder_name = f"{container_id}_{titolo_pulito}"
            working_folder = os.path.join(output_base, base_folder_name)
            # Se la cartella esiste già, aggiungi suffisso univoco
            if os.path.exists(working_folder):
                i = 2
                while True:
                    candidate = os.path.join(output_base, f"{base_folder_name}_rec{i}")
                    if not os.path.exists(candidate):
                        working_folder = candidate
                        break
                    i += 1
            os.makedirs(working_folder, exist_ok=True)

            # Determina referer in base al portale (per header HTTP corretti)
            portale_key = normalize_portal_key(self.portale)
            ark_url_lower = str(self.ark_url).lower() if self.ark_url else ""
            logger.info(f"[DEBUG] _fetch_manifest: portale_key={portale_key}")

            # Forza riconoscimento BNCF dall'URL (case-insensitive, accetta anche https/http)
            if "bncf.firenze.sbn.it" in ark_url_lower or "teca.bncf.firenze.sbn.it" in ark_url_lower:
                logger.info(f"[DEBUG] _fetch_manifest: MATCH BNCF URL trovato in ark_url_lower={ark_url_lower}")
                portale_key = "bncf_teca"

            referer = get_portal_referer(portale_key, ark_url_lower)

            # --- BNCF Teca (Firenze): manifest sintetico prioritario ---
            if portale_key == "bncf_teca":
                from manifest_utils import build_bncf_teca_synthetic_manifest, _build_bncf_teca_manifest, download_bncf_images_brute_force
                logger.info(f"[BNCF] Attivazione logica specifica per {self.ark_url}")
                # Proviamo il sintetico come prima scelta per massima robustezza
                manifest = build_bncf_teca_synthetic_manifest(self.ark_url, working_folder)
                if manifest and isinstance(manifest, dict):
                    os.makedirs(working_folder, exist_ok=True)
                    # Use a fixed ID for the manifest filename to avoid regex issues with BNCF IDs
                    safe_id = re.search(r'idr=([A-Za-z0-9]+)', self.ark_url).group(1) if "idr=" in self.ark_url else "BNCF"
                    manifest_filename = f"manifest_{safe_id}_{titolo_pulito}.json"
                    manifest_path = os.path.join(working_folder, manifest_filename)
                    with open(manifest_path, 'w', encoding='utf-8') as _f:
                        json.dump(manifest, _f, ensure_ascii=False, indent=2)
                    self.manifest_path = manifest_path
                    self.output_dir = working_folder
                    n_canvas = len(manifest['sequences'][0]['canvases'])
                    logger.info(f"[BNCF] Manifest sintetico generato e salvato: {manifest_path} ({n_canvas} immagini)")
                    return manifest
                else:
                    logger.warning("[BNCF] Fallito build sintetico, provo download diretto immagini brute-force...")
                    # Estrai idr
                    m = re.search(r'idr=([A-Za-z0-9]+)', self.ark_url)
                    if not m:
                        logger.error(f"[BNCF] Impossibile estrarre idr da URL: {self.ark_url}")
                        return None
                    idr = m.group(1)
                    # Determina modalità (registro o documento singolo)
                    modalita = getattr(self, 'record_type', 'R')
                    # Range pagine opzionale
                    seq_start = int(getattr(self, 'canvas_da', 1) or 1)
                    seq_end = getattr(self, 'canvas_a', None)
                    seq_end = int(seq_end) if seq_end is not None else None
                    single_seq = seq_start if modalita == 'D' else 1
                    logger.info(f"[BNCF] Avvio download diretto immagini brute-force: idr={idr}, modalita={modalita}, seq_start={seq_start}, seq_end={seq_end}")
                    n_img = download_bncf_images_brute_force(idr, working_folder, modalita=modalita, seq_start=seq_start, seq_end=seq_end, single_seq=single_seq)
                    if n_img > 0:
                        logger.info(f"[BNCF] Download diretto completato: {n_img} immagini scaricate in {working_folder}")
                        # Costruisci manifest minimale per compatibilità pipeline
                        manifest = {
                            "@context": "http://iiif.io/api/presentation/2/context.json",
                            "@id": f"synthetic-bncf-{idr}",
                            "@type": "sc:Manifest",
                            "label": f"BNCF Teca - {idr} (BruteForce)",
                            "sequences": [{
                                "@type": "sc:Sequence",
                                "canvases": [
                                    {
                                        "@id": f"canvas-{idr}-{i}",
                                        "@type": "sc:Canvas",
                                        "label": f"Pagina {i}",
                                        "images": [{
                                            "@type": "oa:Annotation",
                                            "motivation": "sc:painting",
                                            "resource": {
                                                "@id": f"{working_folder}/{idr}_page_{i}.jpg",
                                                "@type": "dctypes:Image",
                                                "format": "image/jpeg"
                                            },
                                            "on": f"canvas-{idr}-{i}"
                                        }]
                                    } for i in range(seq_start, seq_start + n_img)
                                ]
                            }]
                        }
                        self.manifest_path = None  # Non c'è un file manifest, ma la pipeline può proseguire
                        self.output_dir = working_folder
                        return manifest
                    else:
                        logger.error("[BNCF] Download diretto immagini brute-force fallito: nessuna immagine trovata")
                        return None

            # --- Matricula Online: manifest sintetico da HTML scraping ---
            if portale_key == "matricula":
                from manifest_utils import build_matricula_synthetic_manifest
                _scraped_html = getattr(self, '_scraped_html', None)
                manifest = build_matricula_synthetic_manifest(self.ark_url, html=_scraped_html)
                if manifest:
                    os.makedirs(working_folder, exist_ok=True)
                    manifest_filename = f"manifest_{container_id}_{titolo_pulito}.json"
                    manifest_path = os.path.join(working_folder, manifest_filename)
                    with open(manifest_path, 'w', encoding='utf-8') as _f:
                        json.dump(manifest, _f, ensure_ascii=False, indent=2)
                    self.manifest_path = manifest_path
                    self.output_dir = working_folder
                    n_canvas = len(manifest['sequences'][0]['canvases'])
                    logger.info(f"[Matricula] Manifest sintetico salvato: {manifest_path} ({n_canvas} canvas)")
                    return manifest
                else:
                    logger.error("[Matricula] Impossibile costruire manifest sintetico per Matricula Online")
                    return None

            # --- findbuch.net: manifest sintetico da HTML scraping ---
            if portale_key == "findbuch":
                from manifest_utils import build_findbuch_synthetic_manifest
                manifest = build_findbuch_synthetic_manifest(self.ark_url)
                if manifest:
                    os.makedirs(working_folder, exist_ok=True)
                    manifest_filename = f"manifest_{container_id}_{titolo_pulito}.json"
                    manifest_path = os.path.join(working_folder, manifest_filename)
                    with open(manifest_path, 'w', encoding='utf-8') as _f:
                        json.dump(manifest, _f, ensure_ascii=False, indent=2)
                    self.manifest_path = manifest_path
                    self.output_dir = working_folder
                    n_canvas = len(manifest['sequences'][0]['canvases'])
                    logger.info(f"[Findbuch] Manifest sintetico salvato: {manifest_path} ({n_canvas} canvas)")
                    return manifest
                else:
                    logger.error("[Findbuch] Impossibile costruire manifest sintetico per findbuch.net")
                    return None

            # --- Internet Archive: manifest sintetico (iiif.archivelab.org è down) ---
            if portale_key == "internet_archive":
                from manifest_utils import build_ia_synthetic_manifest
                manifest = build_ia_synthetic_manifest(self.ark_url)
                if manifest:
                    os.makedirs(working_folder, exist_ok=True)
                    manifest_filename = f"manifest_{container_id}_{titolo_pulito}.json"
                    manifest_path = os.path.join(working_folder, manifest_filename)
                    with open(manifest_path, 'w', encoding='utf-8') as _f:
                        json.dump(manifest, _f, ensure_ascii=False, indent=2)
                    self.manifest_path = manifest_path
                    self.output_dir = working_folder
                    n_canvas = len(manifest['sequences'][0]['canvases'])
                    logger.info(f"[IA] Manifest sintetico salvato: {manifest_path} ({n_canvas} canvas)")
                    return manifest
                else:
                    logger.error("[IA] Impossibile costruire manifest sintetico per Internet Archive")
                    return None

            # --- BNC Roma: manifest sintetico da HTML item-level ---
            if portale_key == "bnc_roma":
                from manifest_utils import build_bnc_roma_synthetic_manifest
                _scraped_html = getattr(self, '_scraped_html', None)
                manifest = build_bnc_roma_synthetic_manifest(self.ark_url, html=_scraped_html)
                if manifest:
                    os.makedirs(working_folder, exist_ok=True)
                    manifest_filename = f"manifest_{container_id}_{titolo_pulito}.json"
                    manifest_path = os.path.join(working_folder, manifest_filename)
                    with open(manifest_path, 'w', encoding='utf-8') as _f:
                        json.dump(manifest, _f, ensure_ascii=False, indent=2)
                    self.manifest_path = manifest_path
                    self.output_dir = working_folder
                    n_canvas = len(manifest['sequences'][0]['canvases'])
                    logger.info(f"[BNC] Manifest sintetico salvato: {manifest_path} ({n_canvas} canvas)")
                    return manifest
                else:
                    logger.error("[BNC] Impossibile costruire manifest sintetico per BNC Roma")
                    return None

            # --- Biblioteca Digitale Trentina: manifest sintetico da immagini pubbliche ---
            if portale_key == "biblioteca_digitale_trentina":
                from manifest_utils import build_biblioteca_digitale_trentina_synthetic_manifest
                _scraped_html = getattr(self, '_scraped_html', None)
                manifest = build_biblioteca_digitale_trentina_synthetic_manifest(self.ark_url, html=_scraped_html)
                if manifest:
                    os.makedirs(working_folder, exist_ok=True)
                    bdt_id_match = re.search(r"/(?:Iconografia|Testi-a-stampa)/(\d+)", self.ark_url, re.IGNORECASE)
                    bdt_id = bdt_id_match.group(1) if bdt_id_match else container_id
                    manifest_filename = f"manifest_bdt_{bdt_id}_{titolo_pulito}.json"
                    manifest_path = os.path.join(working_folder, manifest_filename)
                    with open(manifest_path, 'w', encoding='utf-8') as _f:
                        json.dump(manifest, _f, ensure_ascii=False, indent=2)
                    self.manifest_path = manifest_path
                    self.output_dir = working_folder
                    n_canvas = len(manifest['sequences'][0]['canvases'])
                    logger.info(f"[BDT] Manifest sintetico salvato: {manifest_path} ({n_canvas} canvas)")
                    return manifest
                else:
                    logger.error("[BDT] Impossibile costruire manifest sintetico")
                    return None

            # --- Biblioteca Digitale Lombarda: PDF REST pubblico puntuale ---
            if portale_key == "biblioteca_digitale_lombarda":
                from manifest_utils import build_biblioteca_digitale_lombarda_pdf_manifest
                manifest = build_biblioteca_digitale_lombarda_pdf_manifest(self.ark_url)
                if manifest:
                    os.makedirs(working_folder, exist_ok=True)
                    bdl_id_match = re.search(r"/bdl/public/rest/srv/item/(\d+)/pdf", self.ark_url, re.IGNORECASE)
                    bdl_id = bdl_id_match.group(1) if bdl_id_match else container_id
                    manifest_filename = f"manifest_bdl_{bdl_id}_{titolo_pulito}.json"
                    manifest_path = os.path.join(working_folder, manifest_filename)
                    with open(manifest_path, 'w', encoding='utf-8') as _f:
                        json.dump(manifest, _f, ensure_ascii=False, indent=2)
                    self.manifest_path = manifest_path
                    self.output_dir = working_folder
                    logger.info(f"[BDL] Manifest sintetico PDF salvato: {manifest_path}")
                    return manifest
                logger.error("[BDL] URL non compatibile con PDF REST pubblico")
                return None

            # --- Rovereto Digital Library: manifest sintetico da API DSpace-GLAM ---
            if portale_key == "rovereto_digital_library":
                from manifest_utils import build_rovereto_synthetic_manifest
                manifest = build_rovereto_synthetic_manifest(self.ark_url)
                if manifest:
                    os.makedirs(working_folder, exist_ok=True)
                    rovereto_id_match = re.search(
                        r"/(?:entities/[a-z-]+|server/api/core/items)/([0-9a-f-]{36})",
                        self.ark_url,
                        re.IGNORECASE,
                    )
                    rovereto_id = rovereto_id_match.group(1) if rovereto_id_match else container_id
                    manifest_filename = f"manifest_rovereto_{rovereto_id}_{titolo_pulito}.json"
                    manifest_path = os.path.join(working_folder, manifest_filename)
                    with open(manifest_path, 'w', encoding='utf-8') as _f:
                        json.dump(manifest, _f, ensure_ascii=False, indent=2)
                    self.manifest_path = manifest_path
                    self.output_dir = working_folder
                    n_canvas = len(manifest['sequences'][0]['canvases'])
                    logger.info(f"[Rovereto] Manifest sintetico salvato: {manifest_path} ({n_canvas} canvas)")
                    return manifest
                logger.error("[Rovereto] Impossibile costruire manifest sintetico")
                return None

            # --- Museogalileo Digiteca: manifest sintetico da TecaService ---
            if portale_key == "museogalileo":
                from manifest_utils import build_museogalileo_synthetic_manifest
                manifest = build_museogalileo_synthetic_manifest(self.ark_url)
                if manifest:
                    os.makedirs(working_folder, exist_ok=True)
                    manifest_filename = f"manifest_{container_id}_{titolo_pulito}.json"
                    manifest_path = os.path.join(working_folder, manifest_filename)
                    with open(manifest_path, 'w', encoding='utf-8') as _f:
                        json.dump(manifest, _f, ensure_ascii=False, indent=2)
                    self.manifest_path = manifest_path
                    self.output_dir = working_folder
                    n_canvas = len(manifest['sequences'][0]['canvases'])
                    logger.info(f"[Museogalileo] Manifest sintetico salvato: {manifest_path} ({n_canvas} canvas)")
                    return manifest
                else:
                    logger.error("[Museogalileo] Impossibile costruire manifest sintetico")
                    return None

            # --- BNCF Teca (Firenze): manifest sintetico se IIIF standard fallisce ---
            if portale_key == "bncf_teca":
                from manifest_utils import build_bncf_teca_synthetic_manifest, _build_bncf_teca_manifest
                # Proviamo prima se c'è un manifest IIIF standard valido (HEAD check)
                std_url = _build_bncf_teca_manifest(self.ark_url)
                if std_url:
                    try:
                        import requests
                        _rh = requests.head(std_url, timeout=5, headers={"User-Agent": "Mozilla/5.0"})
                        if _rh.ok:
                            # Se esiste, procediamo col download standard sotto
                            pass 
                        else:
                            # Altrimenti forziamo il sintetico qui
                            manifest = build_bncf_teca_synthetic_manifest(self.ark_url, working_folder)
                    except:
                        manifest = build_bncf_teca_synthetic_manifest(self.ark_url, working_folder)
                else:
                    manifest = build_bncf_teca_synthetic_manifest(self.ark_url, working_folder)

                if manifest and isinstance(manifest, dict):
                    os.makedirs(working_folder, exist_ok=True)
                    manifest_filename = f"manifest_{container_id}_{titolo_pulito}.json"
                    manifest_path = os.path.join(working_folder, manifest_filename)
                    with open(manifest_path, 'w', encoding='utf-8') as _f:
                        json.dump(manifest, _f, ensure_ascii=False, indent=2)
                    self.manifest_path = manifest_path
                    self.output_dir = working_folder
                    n_canvas = len(manifest['sequences'][0]['canvases'])
                    logger.info(f"[BNCF] Manifest sintetico salvato: {manifest_path} ({n_canvas} canvas)")
                    return manifest

            # --- Internet Culturale / Estense: manifest sintetico da magparser ---
            if portale_key == "internetculturale_estense":
                from manifest_utils import build_internetculturale_estense_synthetic_manifest
                manifest = build_internetculturale_estense_synthetic_manifest(self.ark_url)
                if manifest:
                    os.makedirs(working_folder, exist_ok=True)
                    manifest_filename = f"manifest_{container_id}_{titolo_pulito}.json"
                    manifest_path = os.path.join(working_folder, manifest_filename)
                    with open(manifest_path, 'w', encoding='utf-8') as _f:
                        json.dump(manifest, _f, ensure_ascii=False, indent=2)
                    self.manifest_path = manifest_path
                    self.output_dir = working_folder
                    n_canvas = len(manifest['sequences'][0]['canvases'])
                    logger.info(f"[InternetCulturale] Manifest sintetico salvato: {manifest_path} ({n_canvas} canvas)")
                    return manifest
                else:
                    logger.error("[InternetCulturale] Impossibile costruire manifest sintetico")
                    return None

            # Scarica manifest (requests, con referer del portale)
            manifest = download_manifest(manifest_url, working_folder, self.nome_file, referer=referer)

            # Fallback Playwright: portali con TLS fingerprinting (es. Gallica)
            if not manifest and portale_key != "antenati":
                logger.info(f"[Manifest] requests fallito per {self.portale}, provo Playwright")
                try:
                    from browser_setup import fetch_manifest_json_via_playwright
                    manifest = fetch_manifest_json_via_playwright(manifest_url)
                    if manifest:
                        manifest = normalize_iiif_manifest_for_processing(manifest)
                        # Salva su disco (stessa logica di download_manifest)
                        os.makedirs(working_folder, exist_ok=True)
                        manifest_filename_pw = f"manifest_{container_id}_{titolo_pulito}.json"
                        manifest_path_pw = os.path.join(working_folder, manifest_filename_pw)
                        with open(manifest_path_pw, "w", encoding="utf-8") as _fh:
                            json.dump(manifest, _fh, ensure_ascii=False, indent=2)
                        logger.info(f"[Manifest] Salvato via Playwright: {manifest_path_pw}")
                except Exception as _e:
                    logger.error(f"[Manifest] Playwright fallback errore: {_e}")

            if not manifest:
                logger.error("[Error] Download manifest fallito")
                return None

            # Determina percorso manifest (same logic as download_manifest)
            manifest_filename = f"manifest_{container_id}_{titolo_pulito}.json"
            self.manifest_path = os.path.join(working_folder, manifest_filename)
            self.output_dir = working_folder  # Aggiorna output_dir a cartella di lavoro

            logger.info(f"[OK] Manifest caricato: {self.manifest_path}")
            return manifest
        except Exception as e:
            logger.error(f"[Error] Errore fetch manifest: {e}", exc_info=True)
            return None

    def _get_manifest_url(self):
        """Ricava URL manifest da selenium/playwright o mappatura hardcoded."""
        from manifest_utils import resolve_manifest_url as _resolve_manifest_url

        # Shortcut: portale manifest_diretto → l'URL fornito è già il manifest
        portale_key = self.portale.lower().replace("-", "_").replace(" ", "_")
        manifest_from_viewer = extract_manifest_url_from_viewer_url(self.ark_url)
        if manifest_from_viewer:
            logger.info(f"[Manifest] manifestId estratto dal viewer: {manifest_from_viewer}")
            return manifest_from_viewer

        if portale_key == "manifest_diretto":
            logger.info(f"[Manifest] manifest_diretto: uso URL diretto {self.ark_url}")
            return self.ark_url

        # Shortcut: URL è già un manifest IIIF diretto (.json o /manifest)
        _url_lower = self.ark_url.lower().rstrip("/")
        if _url_lower.endswith(".json") or "/manifest/" in _url_lower or _url_lower.endswith("/manifest"):
            logger.info(f"[Manifest] URL è già un manifest diretto: {self.ark_url}")
            return self.ark_url

        # Tentativo 1: costruzione diretta per portale noto.
        # Evita browser headless quando il portale ha un pattern stabile e testato.
        manifest_direct = _resolve_manifest_url(self.ark_url, self.portale)
        if manifest_direct:
            logger.info(f"[Manifest] resolve_manifest_url ({self.portale}): {manifest_direct}")
            return manifest_direct

        # Antenati espone il manifest DAM nell'HTML pubblico della pagina.
        # Proviamo prima il percorso HTTP leggero, lasciando i browser automatici
        # come fallback per i casi in cui il markup non sia direttamente leggibile.
        if portale_key == "antenati":
            try:
                manifest_http = robust_find_manifest(self.ark_url)
                if manifest_http:
                    logger.info(f"Manifest trovato (HTTP): {manifest_http}")
                    return manifest_http
            except Exception as e:
                logger.debug(f"[Manifest HTTP] Errore: {e}")

        # Tentativo 2: Prova browser automation
        try:
            driver = setup_selenium()
            if driver:
                driver.get(self.ark_url)
                import time
                time.sleep(3)
                html = driver.page_source
                driver.quit()
                self._scraped_html = html  # conserva per Matricula e altri portali
                manifest_url = robust_find_manifest(self.ark_url, html)
                if manifest_url:
                    logger.info(f"Manifest trovato (Selenium): {manifest_url}")
                    return manifest_url
        except Exception as e:
            logger.debug(f"[Selenium] Errore: {e}")

        # Tentativo 2: Fallback Playwright
        try:
            html = setup_playwright(self.ark_url)
            if html:
                self._scraped_html = html  # conserva per Matricula e altri portali
                manifest_url = robust_find_manifest(self.ark_url, html)
                if manifest_url:
                    logger.info(f"Manifest trovato (Playwright): {manifest_url}")
                    return manifest_url
        except Exception as e:
            logger.debug(f"[Playwright] Errore: {e}")

        # Tentativo 4: Usa mappatura hardcoded o costruzione URL standard
        logger.info("Usando fallback build_manifest_url (mappatura hardcoded)")
        try:
            manifest_url = build_manifest_url(self.ark_url)
            logger.info(f"Manifest URL costruito: {manifest_url}")
            return manifest_url
        except Exception as e:
            logger.error(f"Errore build_manifest_url: {e}")
            return None

    def _has_canvas_range_filter(self):
        return getattr(self, 'canvas_da', None) is not None or getattr(self, 'canvas_a', None) is not None

    def _portal_key(self):
        return str(getattr(self, "portale", "") or "").strip().lower().replace("-", "_").replace(" ", "_")

    def _download_bdt_direct_pdf(self, pdf_url: str):
        """Scarica il PDF diretto ufficiale BDT quando l'utente richiede solo PDF."""
        return self._download_direct_pdf(
            pdf_url,
            portal_label="BDT",
            referer="https://bdt.bibcom.trento.it/",
            default_name="documento_bdt",
        )

    def _download_direct_pdf(self, pdf_url: str, portal_label: str, referer: str, default_name: str):
        """Scarica un PDF diretto ufficiale quando l'utente richiede solo PDF."""
        if not pdf_url:
            return False

        try:
            os.makedirs(self.output_dir, exist_ok=True)
            safe_name = re.sub(r'[\\/*?:"<>|]', "", self.nome_file).replace(" ", "_").strip("_")
            if not safe_name:
                safe_name = default_name
            pdf_filename = f"{safe_name}.pdf"
            pdf_path = os.path.join(self.output_dir, pdf_filename)
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Referer': referer,
            }

            response = requests.get(pdf_url, headers=headers, timeout=60)
            if not response.ok:
                logger.error(f"[{portal_label}] PDF diretto non disponibile: HTTP {response.status_code} {pdf_url[:100]}")
                return False

            content = response.content or b""
            content_type = response.headers.get("Content-Type", "").lower()
            if not content or ("pdf" not in content_type and not content.lstrip().startswith(b"%PDF")):
                logger.error(f"[{portal_label}] Risposta PDF non valida: Content-Type={content_type or '?'} url={pdf_url[:100]}")
                return False

            with open(pdf_path, "wb") as pdf_file:
                pdf_file.write(content)

            logger.info(f"[{portal_label}] PDF diretto salvato: {pdf_path} ({len(content)} byte)")
            if self.manifest_path and os.path.exists(self.manifest_path):
                try:
                    estrai_metadati_da_manifest(
                        self.manifest_path,
                        record_prefix=self.record_type,
                        record_url=self.ark_url,
                        record_nome_file=self.nome_file,
                        immagini_generate=[pdf_filename],
                    )
                except Exception as meta_error:
                    logger.warning(f"[{portal_label}] Metadati PDF diretto non aggiornati: {meta_error}")
            return True
        except Exception as exc:
            logger.error(f"[{portal_label}] Errore download PDF diretto: {exc}", exc_info=True)
            return False

    def _process_document(self, tiles_info, metadata):
        """Elabora documento singolo (D/d) con verifica immagini finali e richiesta PDF opzionale."""
        try:
            os.makedirs(self.output_dir, exist_ok=True)
            # Calcola formati (incluso PDF) all'inizio per logica placeholder e salvataggio
            formats = self.formats if hasattr(self, 'formats') and self.formats else state.get('formats', [])
            if not formats:
                formats = ['PNG', 'JPEG', 'TIFF']
            _norm_formats = [_normalize_format(f) for f in formats]
            pdf_in_formats = 'PDF' in _norm_formats
            image_formats = [f for f in formats if _normalize_format(f) != 'PDF']
            only_pdf = pdf_in_formats and not image_formats
            if only_pdf and not self._has_canvas_range_filter():
                if self._portal_key() == "biblioteca_digitale_trentina":
                    bdt_pdf_url = _find_bdt_direct_pdf_url(tiles_info, manifest=self.manifest)
                    if bdt_pdf_url:
                        return self._download_bdt_direct_pdf(bdt_pdf_url)
                if self._portal_key() == "biblioteca_digitale_lombarda":
                    bdl_pdf_url = _find_direct_pdf_url(
                        tiles_info,
                        manifest=self.manifest,
                        allowed_contexts={"bdl_direct_pdf"},
                    )
                    if bdl_pdf_url:
                        return self._download_direct_pdf(
                            bdl_pdf_url,
                            portal_label="BDL",
                            referer="https://www.bdl.servizirl.it/",
                            default_name="documento_bdl",
                        )
            temp_pdf_dir = os.path.join(self.output_dir, "_tmp_pdf_images") if only_pdf else None
            if temp_pdf_dir:
                os.makedirs(temp_pdf_dir, exist_ok=True)
            # ...estrazione canvas come prima...
            target_canvas_id = None
            if "an_ud" in self.ark_url:
                logger.info("[Canvas] Estrazione UD - Lettura canvasId dalla pagina ARK")
                target_canvas_id = extract_canvas_id_from_url(self.ark_url)
                logger.info(f"[Canvas] Risultato estrazione HTML: {target_canvas_id}")
                if not target_canvas_id:
                    logger.warning("[Canvas] Estrazione HTML fallita, provo viewer IIIF")
                try:
                    if not target_canvas_id:
                        target_canvas_id = extract_ud_canvas_id_from_infojson_xhr(self.ark_url, timeout_ms=30000)
                        logger.info(f"[Canvas] Risultato estrazione Playwright: {target_canvas_id}")
                except Exception as e:
                    logger.warning(f"[Canvas] Estrazione Playwright fallita: {e}")
            else:
                target_canvas_id = extract_canvas_id_from_url(self.ark_url)
            if not target_canvas_id:
                if tiles_info:
                    target_canvas_id = _last_segment(tiles_info[0].get("@id") or tiles_info[0].get("id") or "")
                    logger.warning(f"[Canvas] Estrazione canvas ID fallita, uso fallback primo canvas: {target_canvas_id}")
            if not target_canvas_id:
                logger.error("[Error] Impossibile ricavare canvas ID documento (strict mode).")
                return False
            canvas = None
            for c in tiles_info:
                canvas_id = c.get("@id") or c.get("id") or ""
                if target_canvas_id in canvas_id:
                    canvas = c
                    break
            if not canvas:
                if tiles_info:
                    canvas = tiles_info[0]
                    canvas_id = canvas.get("@id") or canvas.get("id") or "(sconosciuto)"
                    logger.warning(f"[Canvas] {target_canvas_id} non trovato, uso primo canvas {canvas_id}")
                else:
                    logger.error(f"[Error] Canvas {target_canvas_id} non trovato nel manifest")
                    return False
            service_info = canvas['images'][0]['resource'].get('service')
            service_id = service_info[0].get('@id') if isinstance(service_info, list) else service_info.get('@id')
            image_info_url = service_id.rstrip('/') + '/info.json'
            logger.info(f"[Canvas] Service ID: {service_id}")
            logger.info(f"[Canvas] Info URL: {image_info_url}")

            # --- IA: download diretto senza IIIF tiles ---
            if service_id and 'BookReaderImages.php' in service_id:
                from io import BytesIO as _BytesIO
                import requests as _req
                _h_ia = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124.0.0.0 Safari/537.36'}
                _r_ia = _req.get(service_id, headers=_h_ia, timeout=45)
                if not _r_ia.ok:
                    logger.error(f"[IA] HTTP {_r_ia.status_code} per documento: {service_id[:80]}")
                    return False
                final_img = Image.open(_BytesIO(_r_ia.content)).copy()
                logger.info(f"[IA] Documento scaricato direttamente: {_r_ia.headers.get('content-length','?')} byte")
                ua = _parse_ua_from_url(self.ark_url)
                ark = _parse_ark_from_url(self.ark_url)
                page_label = canvas.get('label', None)
                meta = build_image_metadata(ua=ua, ark=ark, canvas_id="page_1", page_label=page_label, description=self.nome_file, source_url=self.ark_url, atk_version=VERSION)
                formats = self.formats if hasattr(self, 'formats') and self.formats else state.get('formats', [])
                if not formats:
                    formats = ['PNG', 'JPEG', 'TIFF']
                _norm_fmts = [_normalize_format(f) for f in formats]
                _img_fmts = [f for f in formats if _normalize_format(f) != 'PDF']
                _pdf_in_fmts = 'PDF' in _norm_fmts
                if _img_fmts:
                    save_image_variants(final_img, self.output_dir, self.nome_file, _img_fmts, meta=meta)
                if _pdf_in_fmts:
                    _tmp_dir = os.path.join(self.output_dir, "_tmp_pdf_images")
                    os.makedirs(_tmp_dir, exist_ok=True)
                    _tmp_png = os.path.join(_tmp_dir, f"{self.nome_file}_pdftmp.png")
                    final_img.save(_tmp_png, format='PNG')
                    _pdf_out = os.path.join(self.output_dir, f"{self.nome_file}.pdf")
                    create_pdf_from_images(_tmp_dir, _pdf_out)
                    shutil.rmtree(_tmp_dir, ignore_errors=True)
                return True
            # --- Matricula Online: download diretto JPEG ---
            if service_id and 'hosted-images.matricula-online.eu' in service_id:
                from io import BytesIO as _BytesIO
                import requests as _req
                _h_mat = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
                _r_mat = _req.get(service_id, headers=_h_mat, timeout=45)
                if not _r_mat.ok:
                    logger.error(f"[Matricula] HTTP {_r_mat.status_code} per documento: {service_id[:80]}")
                    return False
                final_img = Image.open(_BytesIO(_r_mat.content)).copy()
                logger.info(f"[Matricula] Documento scaricato: {_r_mat.headers.get('content-length','?')} byte")
                ua = _parse_ua_from_url(self.ark_url)
                ark = _parse_ark_from_url(self.ark_url)
                page_label = canvas.get('label', None)
                meta = build_image_metadata(ua=ua, ark=ark, canvas_id="page_1", page_label=page_label, description=self.nome_file, source_url=self.ark_url, atk_version=VERSION)
                formats = self.formats if hasattr(self, 'formats') and self.formats else state.get('formats', [])
                if not formats:
                    formats = ['PNG', 'JPEG', 'TIFF']
                _norm_fmts = [_normalize_format(f) for f in formats]
                _img_fmts = [f for f in formats if _normalize_format(f) != 'PDF']
                _pdf_in_fmts = 'PDF' in _norm_fmts
                if _img_fmts:
                    save_image_variants(final_img, self.output_dir, self.nome_file, _img_fmts, meta=meta)
                if _pdf_in_fmts:
                    _tmp_dir = os.path.join(self.output_dir, "_tmp_pdf_images")
                    os.makedirs(_tmp_dir, exist_ok=True)
                    _tmp_png = os.path.join(_tmp_dir, f"{self.nome_file}_pdftmp.png")
                    final_img.save(_tmp_png, format='PNG')
                    _pdf_out = os.path.join(self.output_dir, f"{self.nome_file}.pdf")
                    create_pdf_from_images(_tmp_dir, _pdf_out)
                    shutil.rmtree(_tmp_dir, ignore_errors=True)
                return True
            svc = canvas.get('images', [{}])[0].get('resource', {}).get('service', {})
            # --- BNC Roma: download diretto JPEG ---
            if isinstance(svc, dict) and svc.get('@context') == 'bnc_direct':
                from io import BytesIO as _BytesIO
                import requests as _req
                _img_url = svc.get('@id') or service_id
                _h_bnc = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
                _r_bnc = _req.get(_img_url, headers=_h_bnc, timeout=45)
                if not _r_bnc.ok:
                    logger.error(f"[BNC] HTTP {_r_bnc.status_code} per documento: {_img_url[:80]}")
                    return False
                final_img = Image.open(_BytesIO(_r_bnc.content)).copy()
                logger.info(f"[BNC] Documento scaricato: {_r_bnc.headers.get('content-length','?')} byte")
                ua = _parse_ua_from_url(self.ark_url)
                ark = _parse_ark_from_url(self.ark_url)
                page_label = canvas.get('label', None)
                meta = build_image_metadata(ua=ua, ark=ark, canvas_id="page_1", page_label=page_label, description=self.nome_file, source_url=self.ark_url, atk_version=VERSION)
                formats = self.formats if hasattr(self, 'formats') and self.formats else state.get('formats', [])
                if not formats:
                    formats = ['PNG', 'JPEG', 'TIFF']
                _norm_fmts = [_normalize_format(f) for f in formats]
                _img_fmts = [f for f in formats if _normalize_format(f) != 'PDF']
                _pdf_in_fmts = 'PDF' in _norm_fmts
                if _img_fmts:
                    save_image_variants(final_img, self.output_dir, self.nome_file, _img_fmts, meta=meta)
                if _pdf_in_fmts:
                    _tmp_dir = os.path.join(self.output_dir, "_tmp_pdf_images")
                    os.makedirs(_tmp_dir, exist_ok=True)
                    _tmp_png = os.path.join(_tmp_dir, f"{self.nome_file}_pdftmp.png")
                    final_img.save(_tmp_png, format='PNG')
                    _pdf_out = os.path.join(self.output_dir, f"{self.nome_file}.pdf")
                    create_pdf_from_images(_tmp_dir, _pdf_out)
                    shutil.rmtree(_tmp_dir, ignore_errors=True)
                return True
            # --- Internet Culturale: download diretto JPEG cacheman ---
            if isinstance(svc, dict) and svc.get('@context') == 'internetculturale_cacheman_direct':
                from io import BytesIO as _BytesIO
                import requests as _req
                _img_url = svc.get('@id') or service_id
                _h_ic = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
                _r_ic = _req.get(_img_url, headers=_h_ic, timeout=45)
                if not _r_ic.ok:
                    logger.error(f"[InternetCulturale] HTTP {_r_ic.status_code} per documento: {_img_url[:80]}")
                    return False
                final_img = Image.open(_BytesIO(_r_ic.content)).copy()
                logger.info(f"[InternetCulturale] Documento scaricato: {_r_ic.headers.get('content-length','?')} byte")
                ua = _parse_ua_from_url(self.ark_url)
                ark = _parse_ark_from_url(self.ark_url)
                page_label = canvas.get('label', None)
                meta = build_image_metadata(ua=ua, ark=ark, canvas_id="page_1", page_label=page_label, description=self.nome_file, source_url=self.ark_url, atk_version=VERSION)
                formats = self.formats if hasattr(self, 'formats') and self.formats else state.get('formats', [])
                if not formats:
                    formats = ['PNG', 'JPEG', 'TIFF']
                _norm_fmts = [_normalize_format(f) for f in formats]
                _img_fmts = [f for f in formats if _normalize_format(f) != 'PDF']
                _pdf_in_fmts = 'PDF' in _norm_fmts
                if _img_fmts:
                    save_image_variants(final_img, self.output_dir, self.nome_file, _img_fmts, meta=meta)
                if _pdf_in_fmts:
                    _tmp_dir = os.path.join(self.output_dir, "_tmp_pdf_images")
                    os.makedirs(_tmp_dir, exist_ok=True)
                    _tmp_png = os.path.join(_tmp_dir, f"{self.nome_file}_pdftmp.png")
                    final_img.save(_tmp_png, format='PNG')
                    _pdf_out = os.path.join(self.output_dir, f"{self.nome_file}.pdf")
                    create_pdf_from_images(_tmp_dir, _pdf_out)
                    shutil.rmtree(_tmp_dir, ignore_errors=True)
                return True
            # --- Biblioteca Digitale Lombarda: solo PDF REST diretto, niente immagini ---
            if isinstance(svc, dict) and svc.get('@context') == 'bdl_direct_pdf':
                formats = self.formats if hasattr(self, 'formats') and self.formats else state.get('formats', [])
                if not formats:
                    formats = ['PNG', 'JPEG', 'TIFF']
                _norm_fmts = [_normalize_format(f) for f in formats]
                _img_fmts = [f for f in formats if _normalize_format(f) != 'PDF']
                if 'PDF' in _norm_fmts and not _img_fmts:
                    return self._download_direct_pdf(
                        svc.get("pdf_url") or svc.get("@id"),
                        portal_label="BDL",
                        referer="https://www.bdl.servizirl.it/",
                        default_name="documento_bdl",
                    )
                logger.error("[BDL] Il supporto attuale consente solo PDF diretto, non immagini o PDF ricostruiti.")
                return False
            # --- Biblioteca Digitale Trentina: download diretto JPEG pubblico ---
            if isinstance(svc, dict) and svc.get('@context') == 'bdt_direct':
                from io import BytesIO as _BytesIO
                import requests as _req
                _img_url = svc.get('@id') or service_id
                _h_bdt = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                    'Referer': 'https://bdt.bibcom.trento.it/',
                }
                _r_bdt = _req.get(_img_url, headers=_h_bdt, timeout=45)
                if not _r_bdt.ok:
                    logger.error(f"[BDT] HTTP {_r_bdt.status_code} per documento: {_img_url[:80]}")
                    return False
                final_img = Image.open(_BytesIO(_r_bdt.content)).copy()
                logger.info(f"[BDT] Documento scaricato: {_r_bdt.headers.get('content-length','?')} byte")
                ua = _parse_ua_from_url(self.ark_url)
                ark = _parse_ark_from_url(self.ark_url)
                page_label = canvas.get('label', None)
                meta = build_image_metadata(ua=ua, ark=ark, canvas_id="page_1", page_label=page_label, description=self.nome_file, source_url=self.ark_url, atk_version=VERSION)
                formats = self.formats if hasattr(self, 'formats') and self.formats else state.get('formats', [])
                if not formats:
                    formats = ['PNG', 'JPEG', 'TIFF']
                _norm_fmts = [_normalize_format(f) for f in formats]
                _img_fmts = [f for f in formats if _normalize_format(f) != 'PDF']
                _pdf_in_fmts = 'PDF' in _norm_fmts
                if _img_fmts:
                    save_image_variants(final_img, self.output_dir, self.nome_file, _img_fmts, meta=meta)
                if _pdf_in_fmts:
                    _tmp_dir = os.path.join(self.output_dir, "_tmp_pdf_images")
                    os.makedirs(_tmp_dir, exist_ok=True)
                    _tmp_png = os.path.join(_tmp_dir, f"{self.nome_file}_pdftmp.png")
                    final_img.save(_tmp_png, format='PNG')
                    _pdf_out = os.path.join(self.output_dir, f"{self.nome_file}.pdf")
                    create_pdf_from_images(_tmp_dir, _pdf_out)
                    shutil.rmtree(_tmp_dir, ignore_errors=True)
                return True
            # --- FICLIT Digital Library: immagine diretta dal manifest Omeka/IIIF ---
            if self._portal_key() == "dl_ficlit":
                _img_url = _ficlit_direct_image_url_from_canvas(canvas)
                if _img_url:
                    final_img, _status, _size = _download_direct_image(_img_url, "https://dl.ficlit.unibo.it/")
                    if final_img is None:
                        logger.error(f"[FICLIT] HTTP {_status} per documento: {_img_url[:100]}")
                        return False
                    logger.info(f"[FICLIT] Documento scaricato da immagine diretta: {_size} byte")
                    ua = _parse_ua_from_url(self.ark_url)
                    ark = _parse_ark_from_url(self.ark_url)
                    page_label = canvas.get('label', None)
                    meta = build_image_metadata(ua=ua, ark=ark, canvas_id="page_1", page_label=page_label, description=self.nome_file, source_url=self.ark_url, atk_version=VERSION)
                    formats = self.formats if hasattr(self, 'formats') and self.formats else state.get('formats', [])
                    _save_direct_image_outputs(final_img, self.output_dir, self.nome_file, formats, meta=meta)
                    return True
            # --- Rovereto Digital Library: download diretto PNG pubblico da DSpace bitstream ---
            if isinstance(svc, dict) and svc.get('@context') == 'rovereto_direct':
                from io import BytesIO as _BytesIO
                import requests as _req
                _img_url = svc.get('@id') or service_id
                _h_rovereto = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                    'Referer': 'https://digitallibrary.bibliotecacivica.rovereto.tn.it/',
                }
                _r_rovereto = _req.get(_img_url, headers=_h_rovereto, timeout=45)
                if not _r_rovereto.ok:
                    logger.error(f"[Rovereto] HTTP {_r_rovereto.status_code} per documento: {_img_url[:80]}")
                    return False
                final_img = Image.open(_BytesIO(_r_rovereto.content)).copy()
                logger.info(f"[Rovereto] Documento scaricato: {_r_rovereto.headers.get('content-length','?')} byte")
                ua = _parse_ua_from_url(self.ark_url)
                ark = _parse_ark_from_url(self.ark_url)
                page_label = canvas.get('label', None)
                meta = build_image_metadata(ua=ua, ark=ark, canvas_id="page_1", page_label=page_label, description=self.nome_file, source_url=self.ark_url, atk_version=VERSION)
                formats = self.formats if hasattr(self, 'formats') and self.formats else state.get('formats', [])
                if not formats:
                    formats = ['PNG', 'JPEG', 'TIFF']
                _norm_fmts = [_normalize_format(f) for f in formats]
                _img_fmts = [f for f in formats if _normalize_format(f) != 'PDF']
                _pdf_in_fmts = 'PDF' in _norm_fmts
                if _img_fmts:
                    save_image_variants(final_img, self.output_dir, self.nome_file, _img_fmts, meta=meta)
                if _pdf_in_fmts:
                    _tmp_dir = os.path.join(self.output_dir, "_tmp_pdf_images")
                    os.makedirs(_tmp_dir, exist_ok=True)
                    _tmp_png = os.path.join(_tmp_dir, f"{self.nome_file}_pdftmp.png")
                    final_img.save(_tmp_png, format='PNG')
                    _pdf_out = os.path.join(self.output_dir, f"{self.nome_file}.pdf")
                    create_pdf_from_images(_tmp_dir, _pdf_out)
                    shutil.rmtree(_tmp_dir, ignore_errors=True)
                return True
            # --- Museogalileo: download diretto JPEG da TecaService ---
            if isinstance(svc, dict) and svc.get('@context') == 'museogalileo_teca_direct':
                from io import BytesIO as _BytesIO
                _img_url = svc.get('@id') or service_id
                _bid_hint = svc.get('bid') if isinstance(svc, dict) else None
                if not _bid_hint:
                    _bid_hint = _museogalileo_extract_bid(self.ark_url)
                _content, _status, _resolved_url = _download_museogalileo_image(_img_url, bid_hint=_bid_hint, timeout=45)
                if not _content:
                    logger.error(f"[Museogalileo] HTTP {_status} per documento: {_resolved_url[:80] if _resolved_url else _img_url[:80]}")
                    return False
                final_img = Image.open(_BytesIO(_content)).copy()
                logger.info(f"[Museogalileo] Documento scaricato: {len(_content)} byte")
                ua = _parse_ua_from_url(self.ark_url)
                ark = _parse_ark_from_url(self.ark_url)
                page_label = canvas.get('label', None)
                meta = build_image_metadata(ua=ua, ark=ark, canvas_id="page_1", page_label=page_label, description=self.nome_file, source_url=self.ark_url, atk_version=VERSION)
                formats = self.formats if hasattr(self, 'formats') and self.formats else state.get('formats', [])
                if not formats:
                    formats = ['PNG', 'JPEG', 'TIFF']
                _norm_fmts = [_normalize_format(f) for f in formats]
                _img_fmts = [f for f in formats if _normalize_format(f) != 'PDF']
                _pdf_in_fmts = 'PDF' in _norm_fmts
                if _img_fmts:
                    save_image_variants(final_img, self.output_dir, self.nome_file, _img_fmts, meta=meta)
                if _pdf_in_fmts:
                    _tmp_dir = os.path.join(self.output_dir, "_tmp_pdf_images")
                    os.makedirs(_tmp_dir, exist_ok=True)
                    _tmp_png = os.path.join(_tmp_dir, f"{self.nome_file}_pdftmp.png")
                    final_img.save(_tmp_png, format='PNG')
                    _pdf_out = os.path.join(self.output_dir, f"{self.nome_file}.pdf")
                    create_pdf_from_images(_tmp_dir, _pdf_out)
                    shutil.rmtree(_tmp_dir, ignore_errors=True)
                return True
            # --- Findbuch: download via gtpc.php con sessione PHP ---
            if isinstance(svc, dict) and svc.get('@context') == 'findbuch_gtpc':
                from io import BytesIO as _BytesIO
                import requests as _req
                _be  = svc['be_id']
                _ve  = svc['ve_id']
                _cnt = svc['count']
                _base = svc['base_url']
                _view = svc['view_url']
                _ua = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:136.0) Gecko/20100101 Firefox/136.0'
                _hdr = {'User-Agent': _ua, 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'}
                _sess = _req.Session()
                _sess.get(_base + 'main.php', headers=_hdr, timeout=15)
                _sess.get(_view, headers={**_hdr, 'Referer': _base + 'main.php'}, timeout=15)
                _r_fb = _sess.get(_base + 'gtpc.php', headers={**_hdr, 'Accept': 'image/jpeg,*/*', 'Referer': _view},
                                  params={'be_id': _be, 've_id': _ve, 'count': _cnt}, timeout=45)
                if not _r_fb.ok or len(_r_fb.content) == 0:
                    logger.error(f"[Findbuch] Errore download documento gtpc be={_be} ve={_ve} count={_cnt}: HTTP {_r_fb.status_code} size={len(_r_fb.content)}")
                    return False
                final_img = Image.open(_BytesIO(_r_fb.content)).copy()
                logger.info(f"[Findbuch] Documento scaricato: {len(_r_fb.content)} byte")
                ua = _parse_ua_from_url(self.ark_url)
                ark = _parse_ark_from_url(self.ark_url)
                page_label = canvas.get('label', None)
                meta = build_image_metadata(ua=ua, ark=ark, canvas_id="page_1", page_label=page_label, description=self.nome_file, source_url=self.ark_url, atk_version=VERSION)
                formats = self.formats if hasattr(self, 'formats') and self.formats else state.get('formats', [])
                if not formats:
                    formats = ['PNG', 'JPEG', 'TIFF']
                _norm_fmts = [_normalize_format(f) for f in formats]
                _img_fmts = [f for f in formats if _normalize_format(f) != 'PDF']
                _pdf_in_fmts = 'PDF' in _norm_fmts
                if _img_fmts:
                    save_image_variants(final_img, self.output_dir, self.nome_file, _img_fmts, meta=meta)
                if _pdf_in_fmts:
                    _tmp_dir = os.path.join(self.output_dir, "_tmp_pdf_images")
                    os.makedirs(_tmp_dir, exist_ok=True)
                    _tmp_png = os.path.join(_tmp_dir, f"{self.nome_file}_pdftmp.png")
                    final_img.save(_tmp_png, format='PNG')
                    _pdf_out = os.path.join(self.output_dir, f"{self.nome_file}.pdf")
                    create_pdf_from_images(_tmp_dir, _pdf_out)
                    shutil.rmtree(_tmp_dir, ignore_errors=True)
                return True
            # --- IIIF normale ---
            info = download_info_json(image_info_url)
            if not info:
                logger.error(f"[Error] Impossibile scaricare info.json da {image_info_url}")
                return False
            logger.info(f"[Tiles] Scaricando tiles da info.json")
            tile_dir = os.path.join(self.output_dir, "tiles_doc")
            os.makedirs(tile_dir, exist_ok=True)
            tiles_ok, tiles_missing = download_tiles(info, tile_dir, portale=self.portale)
            if tiles_missing:
                logger.warning(f"[Elaborazione] Tile mancanti per {self.nome_file}: {len(tiles_missing)}")
                for mf in tiles_missing:
                    logger.warning(f"[Elaborazione] Tile mancante: {mf}")
                self.tiles_missing = tiles_missing
            else:
                self.tiles_missing = []
            logger.info(f"[Rebuild] Ricostruendo immagine dai tiles")
            final_img = rebuild_image(info, tile_dir, source_url=self.ark_url)
            if final_img is None:
                if pdf_in_formats:
                    logger.warning(f"[PDF] Immagine non ricostruita, genero placeholder per {self.nome_file}")
                    final_img = _make_placeholder_image(service_id,
                        glossario_data=self.glossario_data, lingua=self.lingua,
                        canvas_url=canvas.get('@id') or canvas.get('id'))
                else:
                    logger.error(f"[Error] Fallita ricostruzione immagine")
                    return False
            page_label = canvas.get('label', None)
            try:
                if hasattr(self, 'progress_cb') and callable(self.progress_cb):
                    try:
                        self.progress_cb(1, 1, page_label)
                    except Exception:
                        try:
                            self.progress_cb(1, 1)
                        except Exception:
                            pass
            except Exception:
                pass
            ua = _parse_ua_from_url(self.ark_url)
            ark = _parse_ark_from_url(self.ark_url)
            canvas_id_full = canvas.get("@id") or canvas.get("id") or ""
            canvas_tail = _last_segment(service_id) or _last_segment(canvas_id_full) or target_canvas_id
            description = self.nome_file
            meta = build_image_metadata(
                ua=ua,
                ark=ark,
                canvas_id=canvas_tail,
                page_label=page_label,
                description=description,
                source_url=self.ark_url,
                atk_version=VERSION
            )
            formats = self.formats if hasattr(self, 'formats') and self.formats else state.get('formats', [])
            if not formats:
                formats = ['PNG', 'JPEG', 'TIFF']
            # Salvataggio formati immagine (escluso PDF, gestito separatamente)
            if image_formats:
                save_image_variants(final_img, self.output_dir, self.nome_file, image_formats, meta=meta)
            if only_pdf and temp_pdf_dir:
                _pdf_png_path = os.path.join(temp_pdf_dir, f"{self.nome_file}_pdftmp.png")
                try:
                    final_img.save(_pdf_png_path, format='PNG')
                    logger.info(f"[PDF] Salvata PNG temporanea per PDF: {_pdf_png_path}")
                except Exception as _e:
                    logger.error(f"[PDF] Errore salvataggio PNG temporanea: {_e}")
            # Verifica immagini finali e retry (max 3 tentativi, solo per formati immagine)
            _img_norm = [_normalize_format(f) for f in image_formats]
            immagini_attese = [f"{self.nome_file}.{ext.lower()}" for ext in ['png','jpg','tif'] if _normalize_format(ext.upper()) in _img_norm]
            mancanti = [img for img in immagini_attese if not os.path.exists(os.path.join(self.output_dir, img))]
            retry_count = 0
            max_retries = 3
            while mancanti and retry_count < max_retries:
                logger.warning(f"[Verifica] Mancano immagini finali: {mancanti}. Retry {retry_count+1}/{max_retries}")
                final_img = rebuild_image(info, tile_dir, source_url=self.ark_url)
                if final_img is not None:
                    save_image_variants(final_img, self.output_dir, self.nome_file, image_formats, meta=meta)
                mancanti = [img for img in immagini_attese if not os.path.exists(os.path.join(self.output_dir, img))]
                retry_count += 1
            if mancanti:
                logger.error(f"[Verifica] Immagini finali NON generate dopo {max_retries} tentativi: {mancanti}")
                self.immagini_mancanti = mancanti
            else:
                self.immagini_mancanti = []
            shutil.rmtree(tile_dir, ignore_errors=True)
            logger.info(f"[Cleanup] Cartella tiles eliminata: {tile_dir}")
            # Aggiorna metadati manifest con file generati
            if self.manifest_path and os.path.exists(self.manifest_path):
                _nfmts = [_normalize_format(f) for f in image_formats]
                immagini_generate_meta = []
                for _ext, _nfmt in [('png', 'PNG'), ('jpg', 'JPEG'), ('tif', 'TIFF')]:
                    if _nfmt in _nfmts:
                        immagini_generate_meta.append(f"{self.nome_file}.{_ext}")
                estrai_metadati_da_manifest(
                    self.manifest_path,
                    record_prefix="D",
                    record_url=self.ark_url,
                    record_nome_file=self.nome_file,
                    immagini_generate=immagini_generate_meta
                )
            # Richiesta PDF anche per i documenti singoli
            gen_pdf = False
            if pdf_in_formats:
                gen_pdf = True  # PDF già scelto nella maschera formati, nessun popup
            elif hasattr(self, 'force_gen_pdf') and self.force_gen_pdf is not None:
                gen_pdf = bool(self.force_gen_pdf)
            else:
                if hasattr(self, 'ask_pdf_cb') and callable(self.ask_pdf_cb):
                    try:
                        logger.info("[Elaborazione] Invoco callback richiesta PDF per documento singolo")
                        gen_pdf = bool(self.ask_pdf_cb(self.nome_file))
                        self.force_gen_pdf = gen_pdf
                    except Exception as e:
                        logger.error(f"[Elaborazione] Errore callback richiesta PDF: {e}")
                        gen_pdf = False
            if gen_pdf:
                if only_pdf:
                    pdf_path = self._generate_register_pdf(
                        [f"{self.nome_file}_pdftmp.png"], image_dir=temp_pdf_dir)
                elif pdf_in_formats:
                    # PDF + altri formati: usa immagini già in output_dir
                    _pdf_src = []
                    for _ext in ['.tif', '.tiff', '.png', '.jpg', '.jpeg']:
                        _c = self.nome_file + _ext
                        if os.path.exists(os.path.join(self.output_dir, _c)):
                            _pdf_src.append(_c)
                    pdf_path = self._generate_register_pdf(_pdf_src)
                else:
                    pdf_path = self._generate_register_pdf(
                        [os.path.basename(p) for p in immagini_attese
                         if os.path.exists(os.path.join(self.output_dir, p))])
                if pdf_path:
                    logger.info(f"[OK] PDF generato per documento singolo: {pdf_path}")
            if only_pdf and temp_pdf_dir and os.path.exists(temp_pdf_dir):
                shutil.rmtree(temp_pdf_dir, ignore_errors=True)
                logger.info(f"[Cleanup] Cartella temp PDF eliminata: {temp_pdf_dir}")
            logger.info(f"[OK] Documento elaborato: {self.nome_file}")
            return True
        except Exception as e:
            logger.error(f"[Error] Errore elaborazione documento: {e}", exc_info=True)
            return False


    def _process_register(self, tiles_info, metadata):
        """Elabora registro (R/r) in parallelo per canvas."""
        import concurrent.futures
        try:
            logger.info(f"[Elaborazione] _process_register: output_dir={self.output_dir}")
            os.makedirs(self.output_dir, exist_ok=True)
            logger.info(f"[Elaborazione] Cartella output creata/esistente: {self.output_dir}")
            immagini_generate = []
            formats = self.formats if hasattr(self, 'formats') and self.formats else state.get('formats', [])
            if not formats:
                formats = ['PNG', 'JPEG', 'TIFF']
            _norm_formats = [_normalize_format(f) for f in formats]
            pdf_in_formats = 'PDF' in _norm_formats
            image_formats = [f for f in formats if _normalize_format(f) != 'PDF']
            only_pdf = pdf_in_formats and not image_formats
            if only_pdf and not self._has_canvas_range_filter():
                if self._portal_key() == "biblioteca_digitale_trentina":
                    bdt_pdf_url = _find_bdt_direct_pdf_url(tiles_info, manifest=self.manifest)
                    if bdt_pdf_url:
                        return self._download_bdt_direct_pdf(bdt_pdf_url)
            temp_pdf_dir = os.path.join(self.output_dir, "_tmp_pdf_images") if pdf_in_formats else None
            if temp_pdf_dir:
                os.makedirs(temp_pdf_dir, exist_ok=True)

            from threading import Lock
            immagini_lock = Lock()
            def process_canvas(idx, canvas):
                logger.info(f"[Canvas] Elaborazione {idx}/{len(tiles_info)}")

                # Report start of this canvas to caller (worker -> ProgressDialog)
                try:
                    if hasattr(self, 'progress_cb') and callable(self.progress_cb):
                        try:
                            page_label = canvas.get('label', None)
                            self.progress_cb(idx, len(tiles_info), page_label)
                        except Exception:
                            self.progress_cb(idx, len(tiles_info))
                except Exception:
                    pass

                service_info = canvas['images'][0]['resource'].get('service')
                service_id = service_info[0].get('@id') if isinstance(service_info, list) else service_info.get('@id')
                image_info_url = service_id.rstrip('/') + '/info.json'
                nome_base = f"{self.nome_file}_canvas_{idx}"
                tile_dir = os.path.join(self.output_dir, f"tiles_canvas_{idx}")

                try:
                    # --- BNCF Teca: download diretto JPEG con fallback IIIF ---
                    from io import BytesIO as _BytesIO
                    import requests as _req
                    is_bncf_jpeg = False
                    if service_id and 'teca.bncf.firenze.sbn.it/ImageViewer/servlet/ImageViewer' in service_id and 'azione=showImg' in service_id:
                        is_bncf_jpeg = True
                    if is_bncf_jpeg:
                        _h_bncf = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
                        try:
                            _r_bncf = _req.get(service_id, headers=_h_bncf, timeout=45)
                            logger.debug(f"[BNCF][DEBUG] HTTP {_r_bncf.status_code} - Content-Type: {_r_bncf.headers.get('Content-Type','?')} - Size: {len(_r_bncf.content)} byte per canvas {idx}")
                            if _r_bncf.ok and len(_r_bncf.content) > 10000:
                                try:
                                    final_img = Image.open(_BytesIO(_r_bncf.content)).copy()
                                    logger.info(f"[BNCF] Pagina {idx} JPEG diretta scaricata: {len(_r_bncf.content)} byte")
                                except Exception as pil_e:
                                    logger.error(f"[BNCF][ERROR] PIL non riesce ad aprire l'immagine canvas {idx}: {pil_e}")
                                    # Salva risposta raw per debug
                                    raw_path = os.path.join(self.output_dir, f"{nome_base}_raw_response.jpg")
                                    with open(raw_path, "wb") as raw_f:
                                        raw_f.write(_r_bncf.content)
                                    logger.error(f"[BNCF][DEBUG] Risposta raw salvata per canvas {idx}: {raw_path}")
                                    final_img = None
                            else:
                                logger.warning(f"[BNCF] Download diretto fallito (HTTP {_r_bncf.status_code}, size={len(_r_bncf.content)}) per canvas {idx}, fallback su IIIF tiles")
                                # Salva risposta raw per debug
                                raw_path = os.path.join(self.output_dir, f"{nome_base}_raw_response.jpg")
                                with open(raw_path, "wb") as raw_f:
                                    raw_f.write(_r_bncf.content)
                                logger.warning(f"[BNCF][DEBUG] Risposta raw salvata per canvas {idx}: {raw_path}")
                                final_img = None
                        except Exception as _e:
                            logger.warning(f"[BNCF] Errore download diretto JPEG: {_e}, fallback su IIIF tiles")
                            final_img = None
                        if final_img is not None:
                            ua = _parse_ua_from_url(self.ark_url)
                            ark = _parse_ark_from_url(self.ark_url)
                            page_label = canvas.get('label', None)
                            meta = build_image_metadata(ua=ua, ark=ark, canvas_id=f"page_{idx}", page_label=page_label, description=self.nome_file, source_url=self.ark_url, atk_version=VERSION)
                            _use_img = final_img
                            if image_formats:
                                save_image_variants(_use_img, self.output_dir, nome_base, image_formats, meta=meta)
                            if pdf_in_formats:
                                _pdf_png_path = os.path.join(temp_pdf_dir, f"{nome_base}_pdftmp.png")
                                try:
                                    _use_img.save(_pdf_png_path, format='PNG')
                                except Exception as _e:
                                    logger.error(f"[PDF] Errore PNG BNCF JPEG diretto canvas {idx}: {_e}")
                            return  # nessuna cartella tile da pulire
                        # Se il diretto fallisce, prosegue su IIIF tiles (logica sotto)
                    # --- IA: download diretto senza IIIF tiles ---
                    if service_id and 'BookReaderImages.php' in service_id:
                        _h_ia = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124.0.0.0 Safari/537.36'}
                        _r_ia = _req.get(service_id, headers=_h_ia, timeout=45)
                        if _r_ia.ok:
                            final_img = Image.open(_BytesIO(_r_ia.content)).copy()
                            logger.info(f"[IA] Pagina {idx} scaricata: {_r_ia.headers.get('content-length','?')} byte")
                        else:
                            logger.error(f"[IA] HTTP {_r_ia.status_code} per canvas {idx}")
                            final_img = None
                        ua = _parse_ua_from_url(self.ark_url)
                        ark = _parse_ark_from_url(self.ark_url)
                        page_label = canvas.get('label', None)
                        meta = build_image_metadata(ua=ua, ark=ark, canvas_id=f"page_{idx}", page_label=page_label, description=self.nome_file, source_url=self.ark_url, atk_version=VERSION)
                        _use_img = final_img if final_img is not None else _make_placeholder_image(
                            service_id, glossario_data=self.glossario_data, lingua=self.lingua,
                            canvas_url=canvas.get('@id') or canvas.get('id'))
                        if image_formats:
                            save_image_variants(_use_img, self.output_dir, nome_base, image_formats, meta=meta)
                        if pdf_in_formats:
                            _pdf_png_path = os.path.join(temp_pdf_dir, f"{nome_base}_pdftmp.png")
                            try:
                                _use_img.save(_pdf_png_path, format='PNG')
                            except Exception as _e:
                                logger.error(f"[PDF] Errore PNG IA canvas {idx}: {_e}")
                        return  # nessuna cartella tile da pulire
                    # --- Matricula Online: download diretto JPEG ---
                    if service_id and 'hosted-images.matricula-online.eu' in service_id:
                        _h_mat = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
                        _r_mat = _req.get(service_id, headers=_h_mat, timeout=45)
                        if _r_mat.ok:
                            final_img = Image.open(_BytesIO(_r_mat.content)).copy()
                            logger.info(f"[Matricula] Pagina {idx} scaricata: {_r_mat.headers.get('content-length','?')} byte")
                        else:
                            logger.error(f"[Matricula] HTTP {_r_mat.status_code} per canvas {idx}")
                            final_img = None
                        ua = _parse_ua_from_url(self.ark_url)
                        ark = _parse_ark_from_url(self.ark_url)
                        page_label = canvas.get('label', None)
                        meta = build_image_metadata(ua=ua, ark=ark, canvas_id=f"page_{idx}", page_label=page_label, description=self.nome_file, source_url=self.ark_url, atk_version=VERSION)
                        _use_img = final_img if final_img is not None else _make_placeholder_image(
                            service_id, glossario_data=self.glossario_data, lingua=self.lingua,
                            canvas_url=canvas.get('@id') or canvas.get('id'))
                        if image_formats:
                            save_image_variants(_use_img, self.output_dir, nome_base, image_formats, meta=meta)
                        if pdf_in_formats:
                            _pdf_png_path = os.path.join(temp_pdf_dir, f"{nome_base}_pdftmp.png")
                            try:
                                _use_img.save(_pdf_png_path, format='PNG')
                            except Exception as _e:
                                logger.error(f"[PDF] Errore PNG Matricula canvas {idx}: {_e}")
                        return  # nessuna cartella tile da pulire
                    _svc = canvas.get('images', [{}])[0].get('resource', {}).get('service', {})
                    # --- BNC Roma: download diretto JPEG ---
                    if isinstance(_svc, dict) and _svc.get('@context') == 'bnc_direct':
                        from io import BytesIO as _BytesIO
                        import requests as _req
                        _img_url = _svc.get('@id') or service_id
                        _h_bnc = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
                        _r_bnc = _req.get(_img_url, headers=_h_bnc, timeout=45)
                        if _r_bnc.ok and len(_r_bnc.content) > 0:
                            final_img = Image.open(_BytesIO(_r_bnc.content)).copy()
                            logger.info(f"[BNC] Pagina {idx} scaricata: {len(_r_bnc.content)} byte")
                        else:
                            logger.error(f"[BNC] Errore download pagina {idx}: HTTP {_r_bnc.status_code} size={len(_r_bnc.content)}")
                            final_img = None
                        ua = _parse_ua_from_url(self.ark_url)
                        ark = _parse_ark_from_url(self.ark_url)
                        page_label = canvas.get('label', None)
                        meta = build_image_metadata(ua=ua, ark=ark, canvas_id=f"page_{idx}", page_label=page_label, description=self.nome_file, source_url=self.ark_url, atk_version=VERSION)
                        _use_img = final_img if final_img is not None else _make_placeholder_image(
                            str(_svc.get('@id', '')), glossario_data=self.glossario_data, lingua=self.lingua,
                            canvas_url=canvas.get('@id') or canvas.get('id'))
                        if image_formats:
                            save_image_variants(_use_img, self.output_dir, nome_base, image_formats, meta=meta)
                        if pdf_in_formats:
                            _pdf_png_path = os.path.join(temp_pdf_dir, f"{nome_base}_pdftmp.png")
                            try:
                                _use_img.save(_pdf_png_path, format='PNG')
                            except Exception as _e:
                                logger.error(f"[PDF] Errore PNG BNC canvas {idx}: {_e}")
                        return  # nessuna cartella tile da pulire
                    # --- Internet Culturale: download diretto JPEG cacheman ---
                    if isinstance(_svc, dict) and _svc.get('@context') == 'internetculturale_cacheman_direct':
                        from io import BytesIO as _BytesIO
                        import requests as _req
                        _img_url = _svc.get('@id') or service_id
                        _h_ic = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
                        _r_ic = _req.get(_img_url, headers=_h_ic, timeout=45)
                        if _r_ic.ok and len(_r_ic.content) > 0:
                            final_img = Image.open(_BytesIO(_r_ic.content)).copy()
                            logger.info(f"[InternetCulturale] Pagina {idx} scaricata: {len(_r_ic.content)} byte")
                        else:
                            logger.error(f"[InternetCulturale] Errore download pagina {idx}: HTTP {_r_ic.status_code} size={len(_r_ic.content)}")
                            final_img = None
                        ua = _parse_ua_from_url(self.ark_url)
                        ark = _parse_ark_from_url(self.ark_url)
                        page_label = canvas.get('label', None)
                        meta = build_image_metadata(ua=ua, ark=ark, canvas_id=f"page_{idx}", page_label=page_label, description=self.nome_file, source_url=self.ark_url, atk_version=VERSION)
                        _use_img = final_img if final_img is not None else _make_placeholder_image(
                            str(_svc.get('@id', '')), glossario_data=self.glossario_data, lingua=self.lingua,
                            canvas_url=canvas.get('@id') or canvas.get('id'))
                        if image_formats:
                            save_image_variants(_use_img, self.output_dir, nome_base, image_formats, meta=meta)
                        if pdf_in_formats:
                            _pdf_png_path = os.path.join(temp_pdf_dir, f"{nome_base}_pdftmp.png")
                            try:
                                _use_img.save(_pdf_png_path, format='PNG')
                            except Exception as _e:
                                logger.error(f"[PDF] Errore PNG InternetCulturale canvas {idx}: {_e}")
                        return  # nessuna cartella tile da pulire
                    # --- Biblioteca Digitale Trentina: download diretto JPEG pubblico ---
                    if isinstance(_svc, dict) and _svc.get('@context') == 'bdt_direct':
                        from io import BytesIO as _BytesIO
                        import requests as _req
                        _img_url = _svc.get('@id') or service_id
                        _h_bdt = {
                            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                            'Referer': 'https://bdt.bibcom.trento.it/',
                        }
                        _r_bdt = _req.get(_img_url, headers=_h_bdt, timeout=45)
                        if _r_bdt.ok and len(_r_bdt.content) > 0:
                            final_img = Image.open(_BytesIO(_r_bdt.content)).copy()
                            logger.info(f"[BDT] Pagina {idx} scaricata: {len(_r_bdt.content)} byte")
                        else:
                            logger.error(f"[BDT] Errore download pagina {idx}: HTTP {_r_bdt.status_code} size={len(_r_bdt.content)}")
                            final_img = None
                        ua = _parse_ua_from_url(self.ark_url)
                        ark = _parse_ark_from_url(self.ark_url)
                        page_label = canvas.get('label', None)
                        meta = build_image_metadata(ua=ua, ark=ark, canvas_id=f"page_{idx}", page_label=page_label, description=self.nome_file, source_url=self.ark_url, atk_version=VERSION)
                        _use_img = final_img if final_img is not None else _make_placeholder_image(
                            str(_svc.get('@id', '')), glossario_data=self.glossario_data, lingua=self.lingua,
                            canvas_url=canvas.get('@id') or canvas.get('id'))
                        if image_formats:
                            save_image_variants(_use_img, self.output_dir, nome_base, image_formats, meta=meta)
                        if pdf_in_formats:
                            _pdf_png_path = os.path.join(temp_pdf_dir, f"{nome_base}_pdftmp.png")
                            try:
                                _use_img.save(_pdf_png_path, format='PNG')
                            except Exception as _e:
                                logger.error(f"[PDF] Errore PNG BDT canvas {idx}: {_e}")
                        return  # nessuna cartella tile da pulire
                    # --- FICLIT Digital Library: immagine diretta dal manifest Omeka/IIIF ---
                    if self._portal_key() == "dl_ficlit":
                        _img_url = _ficlit_direct_image_url_from_canvas(canvas)
                        final_img = None
                        if _img_url:
                            final_img, _status, _size = _download_direct_image(_img_url, "https://dl.ficlit.unibo.it/")
                            if final_img is not None:
                                logger.info(f"[FICLIT] Pagina {idx} scaricata da immagine diretta: {_size} byte")
                            else:
                                logger.error(f"[FICLIT] Errore download pagina {idx}: HTTP {_status} url={_img_url[:100]}")
                        else:
                            logger.error(f"[FICLIT] Nessuna immagine diretta nel canvas {idx}")
                        ua = _parse_ua_from_url(self.ark_url)
                        ark = _parse_ark_from_url(self.ark_url)
                        page_label = canvas.get('label', None)
                        meta = build_image_metadata(ua=ua, ark=ark, canvas_id=f"page_{idx}", page_label=page_label, description=self.nome_file, source_url=self.ark_url, atk_version=VERSION)
                        _use_img = final_img if final_img is not None else _make_placeholder_image(
                            _img_url or service_id, glossario_data=self.glossario_data, lingua=self.lingua,
                            canvas_url=canvas.get('@id') or canvas.get('id'))
                        if image_formats:
                            save_image_variants(_use_img, self.output_dir, nome_base, image_formats, meta=meta)
                        if pdf_in_formats:
                            _pdf_png_path = os.path.join(temp_pdf_dir, f"{nome_base}_pdftmp.png")
                            try:
                                _use_img.save(_pdf_png_path, format='PNG')
                            except Exception as _e:
                                logger.error(f"[PDF] Errore PNG FICLIT canvas {idx}: {_e}")
                        return  # nessuna cartella tile da pulire
                    # --- Rovereto Digital Library: download diretto PNG pubblico da DSpace bitstream ---
                    if isinstance(_svc, dict) and _svc.get('@context') == 'rovereto_direct':
                        from io import BytesIO as _BytesIO
                        import requests as _req
                        _img_url = _svc.get('@id') or service_id
                        _h_rovereto = {
                            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                            'Referer': 'https://digitallibrary.bibliotecacivica.rovereto.tn.it/',
                        }
                        _r_rovereto = _req.get(_img_url, headers=_h_rovereto, timeout=45)
                        if _r_rovereto.ok and len(_r_rovereto.content) > 0:
                            final_img = Image.open(_BytesIO(_r_rovereto.content)).copy()
                            logger.info(f"[Rovereto] Pagina {idx} scaricata: {len(_r_rovereto.content)} byte")
                        else:
                            logger.error(f"[Rovereto] Errore download pagina {idx}: HTTP {_r_rovereto.status_code} size={len(_r_rovereto.content)}")
                            final_img = None
                        ua = _parse_ua_from_url(self.ark_url)
                        ark = _parse_ark_from_url(self.ark_url)
                        page_label = canvas.get('label', None)
                        meta = build_image_metadata(ua=ua, ark=ark, canvas_id=f"page_{idx}", page_label=page_label, description=self.nome_file, source_url=self.ark_url, atk_version=VERSION)
                        _use_img = final_img if final_img is not None else _make_placeholder_image(
                            str(_svc.get('@id', '')), glossario_data=self.glossario_data, lingua=self.lingua,
                            canvas_url=canvas.get('@id') or canvas.get('id'))
                        if image_formats:
                            save_image_variants(_use_img, self.output_dir, nome_base, image_formats, meta=meta)
                        if pdf_in_formats:
                            _pdf_png_path = os.path.join(temp_pdf_dir, f"{nome_base}_pdftmp.png")
                            try:
                                _use_img.save(_pdf_png_path, format='PNG')
                            except Exception as _e:
                                logger.error(f"[PDF] Errore PNG Rovereto canvas {idx}: {_e}")
                        return  # nessuna cartella tile da pulire
                    # --- Museogalileo: download diretto JPEG da TecaService ---
                    if isinstance(_svc, dict) and _svc.get('@context') == 'museogalileo_teca_direct':
                        from io import BytesIO as _BytesIO
                        _img_url = _svc.get('@id') or service_id
                        _bid_hint = _svc.get('bid') if isinstance(_svc, dict) else None
                        if not _bid_hint:
                            _bid_hint = _museogalileo_extract_bid(self.ark_url)
                        _content, _status, _resolved_url = _download_museogalileo_image(_img_url, bid_hint=_bid_hint, timeout=45)
                        if _content and len(_content) > 0:
                            final_img = Image.open(_BytesIO(_content)).copy()
                            logger.info(f"[Museogalileo] Pagina {idx} scaricata: {len(_content)} byte")
                        else:
                            logger.error(f"[Museogalileo] Errore download pagina {idx}: HTTP {_status} url={_resolved_url or _img_url}")
                            final_img = None
                        ua = _parse_ua_from_url(self.ark_url)
                        ark = _parse_ark_from_url(self.ark_url)
                        page_label = canvas.get('label', None)
                        meta = build_image_metadata(ua=ua, ark=ark, canvas_id=f"page_{idx}", page_label=page_label, description=self.nome_file, source_url=self.ark_url, atk_version=VERSION)
                        _use_img = final_img if final_img is not None else _make_placeholder_image(
                            str(_svc.get('@id', '')), glossario_data=self.glossario_data, lingua=self.lingua,
                            canvas_url=canvas.get('@id') or canvas.get('id'))
                        if image_formats:
                            save_image_variants(_use_img, self.output_dir, nome_base, image_formats, meta=meta)
                        if pdf_in_formats:
                            _pdf_png_path = os.path.join(temp_pdf_dir, f"{nome_base}_pdftmp.png")
                            try:
                                _use_img.save(_pdf_png_path, format='PNG')
                            except Exception as _e:
                                logger.error(f"[PDF] Errore PNG Museogalileo canvas {idx}: {_e}")
                        return  # nessuna cartella tile da pulire
                    # --- Findbuch: download via gtpc.php con sessione PHP ---
                    if isinstance(_svc, dict) and _svc.get('@context') == 'findbuch_gtpc':
                        from io import BytesIO as _BytesIO
                        import requests as _req
                        _be   = _svc['be_id']
                        _ve   = _svc['ve_id']
                        _cnt  = _svc['count']
                        _base = _svc['base_url']
                        _view = _svc['view_url']
                        # Crea sempre una sessione locale per questo canvas (thread-safe)
                        _ua = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:136.0) Gecko/20100101 Firefox/136.0'
                        _hdr = {'User-Agent': _ua, 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'}
                        _sess_fb = _req.Session()
                        _sess_fb.get(_base + 'main.php', headers=_hdr, timeout=15)
                        _sess_fb.get(_view, headers={**_hdr, 'Referer': _base + 'main.php'}, timeout=15)
                        _r_fb = _sess_fb.get(
                            _base + 'gtpc.php',
                            headers={**_hdr, 'Accept': 'image/jpeg,*/*', 'Referer': _view},
                            params={'be_id': _be, 've_id': _ve, 'count': _cnt}, timeout=45)
                        if _r_fb.ok and len(_r_fb.content) > 0:
                            final_img = Image.open(_BytesIO(_r_fb.content)).copy()
                            logger.info(f"[Findbuch] Pagina {idx} scaricata: {len(_r_fb.content)} byte")
                        else:
                            logger.error(f"[Findbuch] Errore gtpc be={_be} ve={_ve} count={_cnt}: HTTP {_r_fb.status_code} size={len(_r_fb.content)}")
                            final_img = None
                        ua = _parse_ua_from_url(self.ark_url)
                        ark = _parse_ark_from_url(self.ark_url)
                        page_label = canvas.get('label', None)
                        meta = build_image_metadata(ua=ua, ark=ark, canvas_id=f"page_{idx}", page_label=page_label, description=self.nome_file, source_url=self.ark_url, atk_version=VERSION)
                        _use_img = final_img if final_img is not None else _make_placeholder_image(
                            str(_svc.get('@id', '')), glossario_data=self.glossario_data, lingua=self.lingua,
                            canvas_url=canvas.get('@id') or canvas.get('id'))
                        if image_formats:
                            save_image_variants(_use_img, self.output_dir, nome_base, image_formats, meta=meta)
                        if pdf_in_formats:
                            _pdf_png_path = os.path.join(temp_pdf_dir, f"{nome_base}_pdftmp.png")
                            try:
                                _use_img.save(_pdf_png_path, format='PNG')
                            except Exception as _e:
                                logger.error(f"[PDF] Errore PNG Findbuch canvas {idx}: {_e}")
                        return  # nessuna cartella tile da pulire
                    # --- IIIF normale ---
                    info = download_info_json(image_info_url)
                    os.makedirs(tile_dir, exist_ok=True)
                    tiles_ok, tiles_missing = download_tiles(info, tile_dir, portale=self.portale)
                    if tiles_missing:
                        logger.warning(f"[Elaborazione] Tile mancanti per {nome_base}: {len(tiles_missing)}")
                        for mf in tiles_missing:
                            logger.warning(f"[Elaborazione] Tile mancante: {mf}")
                        if not hasattr(self, 'tiles_missing_all'):
                            self.tiles_missing_all = []
                        self.tiles_missing_all.extend(tiles_missing)
                    final_img = rebuild_image(info, tile_dir, source_url=self.ark_url)
                    ua = _parse_ua_from_url(self.ark_url)
                    ark = _parse_ark_from_url(self.ark_url)
                    canvas_tail = _last_segment(service_id)
                    page_label = canvas.get('label', None)
                    meta = build_image_metadata(
                        ua=ua,
                        ark=ark,
                        canvas_id=canvas_tail,
                        page_label=page_label,
                        description=self.nome_file,
                        source_url=self.ark_url,
                        atk_version=VERSION
                    )
                    _use_img = final_img if final_img is not None else _make_placeholder_image(
                        service_id, glossario_data=self.glossario_data, lingua=self.lingua,
                        canvas_url=canvas.get('@id') or canvas.get('id'))
                    if image_formats:
                        save_image_variants(_use_img, self.output_dir, nome_base, image_formats, meta=meta)
                    if pdf_in_formats:
                        _pdf_png_path = os.path.join(temp_pdf_dir, f"{nome_base}_pdftmp.png")
                        try:
                            _use_img.save(_pdf_png_path, format='PNG')
                        except Exception as _e:
                            logger.error(f"[PDF] Errore salvataggio PNG canvas {idx}: {_e}")
                    # Elimina la cartella dei tile dopo la ricostruzione
                    shutil.rmtree(tile_dir, ignore_errors=True)
                    logger.info(f"[Cleanup] Cartella tiles eliminata: {tile_dir}")
                except Exception as e:
                    logger.error(f"[Error] Errore canvas {idx}: {e}", exc_info=True)
                    # Genera placeholder per questo canvas e pulisce la cartella tile
                    try:
                        _ph = _make_placeholder_image(service_id, glossario_data=self.glossario_data, lingua=self.lingua,
                        canvas_url=canvas.get('@id') or canvas.get('id'))
                        if image_formats:
                            save_image_variants(_ph, self.output_dir, nome_base, image_formats)
                        if pdf_in_formats:
                            _ph.save(os.path.join(temp_pdf_dir, f"{nome_base}_pdftmp.png"), format='PNG')
                            logger.info(f"[PDF] Placeholder salvato per canvas {idx} fallito")
                    except Exception as _ep:
                        logger.error(f"[Error] Errore salvataggio placeholder canvas {idx}: {_ep}")
                    finally:
                        shutil.rmtree(tile_dir, ignore_errors=True)
                        logger.info(f"[Cleanup] Cartella tiles eliminata (dopo errore): {tile_dir}")

            # Parallelizzazione automatica: rispetta i portali che richiedono accesso sequenziale.
            max_workers = _canvas_max_workers_for_portal(self._portal_key())
            with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
                futures = [executor.submit(process_canvas, idx, canvas) for idx, canvas in enumerate(tiles_info, 1)]
                for f in concurrent.futures.as_completed(futures):
                    pass  # errori già loggati

            # Verifica immagini finali e retry (max 3 tentativi) per tutte le pagine
            _img_norm_r = [_normalize_format(f) for f in image_formats]
            immagini_attese = []
            for idx, canvas in enumerate(tiles_info, 1):
                nome_base = f"{self.nome_file}_canvas_{idx}"
                for ext in ['png','jpg','tif']:
                    if _normalize_format(ext.upper()) in _img_norm_r:
                        immagini_attese.append(f"{nome_base}.{ext}")
            mancanti = [img for img in immagini_attese if not os.path.exists(os.path.join(self.output_dir, img))]
            retry_count = 0
            max_retries = 3
            while mancanti and retry_count < max_retries:
                logger.warning(f"[Verifica] Mancano immagini finali: {mancanti}. Retry {retry_count+1}/{max_retries}")
                # Per ogni pagina mancante, tenta la ricostruzione
                for img in mancanti:
                    # Ricava idx da nome file
                    try:
                        idx_str = img.split('_canvas_')[-1].split('.')[0]
                        idx_canvas = int(idx_str)
                        canvas = tiles_info[idx_canvas-1]
                        service_info = canvas['images'][0]['resource'].get('service')
                        service_id = service_info[0].get('@id') if isinstance(service_info, list) else service_info.get('@id')
                        image_info_url = service_id.rstrip('/') + '/info.json'
                        info = download_info_json(image_info_url)
                        tile_dir = os.path.join(self.output_dir, f"tiles_canvas_{idx_canvas}")
                        final_img = rebuild_image(info, tile_dir, source_url=self.ark_url)
                        nome_base = f"{self.nome_file}_canvas_{idx_canvas}"
                        meta = build_image_metadata(
                            ua=_parse_ua_from_url(self.ark_url),
                            ark=_parse_ark_from_url(self.ark_url),
                            canvas_id=_last_segment(service_id),
                            page_label=canvas.get('label', None),
                            description=self.nome_file,
                            source_url=self.ark_url,
                            atk_version=VERSION
                        )
                        save_image_variants(final_img, self.output_dir, nome_base, image_formats, meta=meta)
                        # Elimina la cartella dei tile dopo la ricostruzione anche nei retry
                        shutil.rmtree(tile_dir, ignore_errors=True)
                        logger.info(f"[Cleanup] Cartella tiles eliminata (retry): {tile_dir}")
                    except Exception as e:
                        logger.error(f"[Retry] Errore retry immagine {img}: {e}")
                mancanti = [img for img in immagini_attese if not os.path.exists(os.path.join(self.output_dir, img))]
                retry_count += 1
            if mancanti:
                logger.error(f"[Verifica] Immagini finali NON generate dopo {max_retries} tentativi: {mancanti}")
                self.immagini_mancanti = mancanti
            else:
                self.immagini_mancanti = []

            # Popola immagini_generate con tutti i file effettivamente prodotti
            # (nota: process_canvas non aggiunge a immagini_generate per thread-safety)
            for _img in immagini_attese:
                if os.path.exists(os.path.join(self.output_dir, _img)):
                    immagini_generate.append(_img)

            logger.info(f"[Elaborazione] File generati: {immagini_generate}")
            # --- RICHIESTA PDF DOPO ULTIMO CANVAS ---
            gen_pdf = False
            if pdf_in_formats:
                gen_pdf = True  # PDF già scelto nella maschera formati, nessun popup
            elif hasattr(self, 'force_gen_pdf') and self.force_gen_pdf is not None:
                gen_pdf = bool(self.force_gen_pdf)
            else:
                if hasattr(self, 'ask_pdf_cb') and callable(self.ask_pdf_cb):
                    try:
                        logger.info("[Elaborazione] Invoco callback richiesta PDF dopo ultimo canvas")
                        gen_pdf = bool(self.ask_pdf_cb(self.nome_file))
                        self.force_gen_pdf = gen_pdf
                    except Exception as e:
                        logger.error(f"[Elaborazione] Errore callback richiesta PDF: {e}")
                        gen_pdf = False

            # Genera PDF
            if gen_pdf:
                if pdf_in_formats:
                    if only_pdf:
                        # Usa immagini temporanee da temp_pdf_dir (ordinate per idx)
                        _pdf_imgs = [
                            f"{self.nome_file}_canvas_{i}_pdftmp.png"
                            for i in range(1, len(tiles_info) + 1)
                            if os.path.exists(os.path.join(temp_pdf_dir,
                               f"{self.nome_file}_canvas_{i}_pdftmp.png"))
                        ]
                        pdf_path = self._generate_register_pdf(_pdf_imgs, image_dir=temp_pdf_dir)
                    else:
                        # PDF + altri formati: usa PNG temporanee da temp_pdf_dir (ordinate per idx)
                        _pdf_imgs = [
                            f"{self.nome_file}_canvas_{i}_pdftmp.png"
                            for i in range(1, len(tiles_info) + 1)
                            if os.path.exists(os.path.join(temp_pdf_dir,
                               f"{self.nome_file}_canvas_{i}_pdftmp.png"))
                        ]
                        pdf_path = self._generate_register_pdf(_pdf_imgs, image_dir=temp_pdf_dir)
                    if pdf_path:
                        immagini_generate.append(os.path.basename(pdf_path))
                else:
                    mancanti_pdf = [img for img in immagini_attese if not os.path.exists(os.path.join(self.output_dir, img))]
                    if mancanti_pdf:
                        try:
                            from user_prompts import ask_generate_pdf_missing_images
                            parent = getattr(self, 'parent', None) if hasattr(self, 'parent') else None
                            glossario = getattr(self, 'glossario_data', None) if hasattr(self, 'glossario_data') else None
                            lingua = getattr(self, 'lingua', 'IT') if hasattr(self, 'lingua') else 'IT'
                            dark_mode = getattr(self, 'dark_mode', False) if hasattr(self, 'dark_mode') else False
                            conferma = ask_generate_pdf_missing_images(len(mancanti_pdf), glossario, lingua, parent, dark_mode)
                        except Exception as e:
                            logger.error(f"[PDF] Errore popup immagini mancanti: {e}")
                            conferma = False
                        if conferma:
                            pdf_path = self._generate_register_pdf([img for img in immagini_attese if os.path.exists(os.path.join(self.output_dir, img))])
                            if pdf_path:
                                immagini_generate.append(os.path.basename(pdf_path))
                        else:
                            logger.error(f"[PDF] PDF NON generato: immagini mancanti: {mancanti_pdf}")
                    else:
                        pdf_path = self._generate_register_pdf(immagini_attese)
                        if pdf_path:
                            immagini_generate.append(os.path.basename(pdf_path))
            if temp_pdf_dir and os.path.exists(temp_pdf_dir):
                shutil.rmtree(temp_pdf_dir, ignore_errors=True)
                logger.info(f"[Cleanup] Cartella temp PDF eliminata: {temp_pdf_dir}")

            # Aggiorna metadati finali
            if self.manifest_path and os.path.exists(self.manifest_path):
                estrai_metadati_da_manifest(
                    self.manifest_path,
                    record_prefix="R",
                    record_url=self.ark_url,
                    record_nome_file=self.nome_file,
                    immagini_generate=immagini_generate
                )

            logger.info(f"[OK] Registro elaborato: {self.nome_file}")
            return True
        except Exception as e:
            logger.error(f"[Error] Errore elaborazione registro: {e}", exc_info=True)
            return False

    def _get_document_canvas_id(self):
        """Ricava canvas ID per documento (D/d)."""
        if "an_ua" in self.ark_url:
            # Documento singolo UA: usa l'ultimo segmento
            logger.info("[Canvas] Tipo: UA - estrazione diretta da URL")
            canvas_id = extract_canvas_id_from_url(self.ark_url)
            logger.info(f"[Canvas] Risultato UA: {canvas_id}")
            return canvas_id
        elif "an_ud" in self.ark_url:
            # Documento UD: intercetta con Playwright
            logger.info("[Canvas] Tipo: UD - estrazione con Playwright")
            try:
                canvas_id = extract_ud_canvas_id_from_infojson_xhr(self.ark_url)
                logger.info(f"[Canvas] Risultato UD: {canvas_id}")
                return canvas_id
            except Exception as e:
                logger.error(f"[Error] Eccezione in extract_ud_canvas_id_from_infojson_xhr: {e}", exc_info=True)
                return None
        return None

    def _generate_register_pdf(self, immagini_generate, image_dir=None):
        """Genera PDF multipagina da immagini registro.
        image_dir: cartella da cui cercare le immagini (default: self.output_dir)."""
        if image_dir is None:
            image_dir = self.output_dir
        try:
            ordered_paths = []
            for img_name in immagini_generate:
                img_path = os.path.join(image_dir, img_name)
                if os.path.exists(img_path):
                    ordered_paths.append(img_path)

            if not ordered_paths:
                logger.warning("[Warning] Nessuna immagine per PDF")
                return None

            titolo_pulito = re.sub(r'[\\/*?:"<>|]', "", self.nome_file).replace(" ", "_")
            pdf_filename = f"{titolo_pulito}.pdf"
            pdf_full_path = os.path.join(self.output_dir, pdf_filename)

            # Filtra le immagini scegliendo una sola variante per pagina
            # Priorità qualitativa: TIFF -> PNG -> JPEG
            try:
                by_base = {}
                for p in ordered_paths:
                    base = os.path.splitext(os.path.basename(p))[0]
                    ext = os.path.splitext(p)[1].lower()
                    if base not in by_base:
                        by_base[base] = {}
                    by_base[base][ext] = p

                preferred_order = ['.tif', '.tiff', '.png', '.jpg', '.jpeg']
                selected_paths = []
                def _canvas_sort_key(name):
                    m = re.search(r'_canvas_(\d+)', name)
                    return int(m.group(1)) if m else 0
                for base in sorted(by_base.keys(), key=_canvas_sort_key):
                    exts_map = by_base[base]
                    chosen = None
                    for pe in preferred_order:
                        if pe in exts_map:
                            chosen = exts_map[pe]
                            break
                    if chosen:
                        selected_paths.append(chosen)

                if not selected_paths:
                    logger.warning("[Warning] Nessuna immagine selezionata dopo filtro priorità formati")
                    return None

                logger.info(f"[PDF] Immagini selezionate per PDF: {len(selected_paths)} pagine (priorità TIFF>PNG>JPEG)")
                pdf_path = create_pdf_from_images(selected_paths, pdf_full_path, resolution_dpi=400)
            except Exception as e:
                logger.error(f"[Error] Errore nel filtrare le immagini per PDF: {e}", exc_info=True)
                return None
            
            if pdf_path:
                # Arricchisci metadati PDF
                ua_doc = _parse_ua_from_url(self.ark_url)
                ark_doc = _parse_ark_from_url(self.ark_url)
                enrich_pdf_metadata(
                    pdf_path=pdf_path,
                    title=self.nome_file,
                    subject=self.nome_file,
                    ua=ua_doc,
                    ark=ark_doc
                )
                logger.info(f"[OK] PDF generato: {pdf_path}")
                return pdf_path

        except Exception as e:
            logger.error(f"[Error] Errore generazione PDF: {e}")

        return None


def esegui_elaborazione(state, glossario_data=None, lingua="IT", records=None, formats=None, parent=None):
    """
    Orchestratore principale per GUI/main: elabora i record caricati.
    Usa records e formats passati o quelli nello stato globale.
    Wrapper che adatta la classe Elaborazione alle interfacce v1.4.1.
    Ora accetta anche un parent opzionale per ProgressDialog.
    """
    if records is None:
        records = state["records"]
    if formats is None:
        formats = state["formats"]
    output_folder = state["output_folder"]
    output_folders_doc = state.get("output_folders_doc", [])
    output_folders_reg = state.get("output_folders_reg", [])
    logger.info(f"[STATO] output_folder: {output_folder}")
    logger.info(f"[STATO] output_folders_doc: {output_folders_doc}")
    logger.info(f"[STATO] output_folders_reg: {output_folders_reg}")
    logger.info(f"[STATO] records: {[{'modalita': r.get('modalita'), 'nome_file': r.get('nome_file'), 'output': r.get('output')} for r in records]}")
    # parent ora è un argomento esplicito

    if not records:
        raise RuntimeError("Nessun record caricato")
    if not formats:
        raise RuntimeError("Nessun formato selezionato")
    if not output_folder and not output_folders_doc and not output_folders_reg:
        raise RuntimeError("Nessuna cartella selezionata")

    risultati = []

    # Prova a mostrare un dialog di progresso se disponibile (PySide6)
    progress = None
    qcore = None
    # Crea ProgressDialog solo se ci sono record da elaborare e solo in modalità Qt (con parent)
    if records and parent is not None:
        try:
            from src.user_prompts import ProgressDialog
            from PySide6.QtCore import QCoreApplication
            progress = ProgressDialog(glossario_data, lingua, total=len(records), parent=parent)
            progress.show()
            qcore = QCoreApplication
            # Forza subito il refresh della GUI per evitare dialog bianco
            if qcore:
                qcore.processEvents()
        except Exception:
            progress = None
            qcore = None
    else:
        progress = None
        qcore = None

    doc_counter = 0
    reg_counter = 0
    n_doc = sum(1 for r in records if str(r.get("modalita", "")).strip().upper() == "D")
    n_reg = sum(1 for r in records if str(r.get("modalita", "")).strip().upper() == "R")
    if output_folders_doc and len(output_folders_doc) not in (1, n_doc):
        logger.warning(f"[Output] Numero cartelle documenti ({len(output_folders_doc)}) diverso dal numero di documenti ({n_doc})")
    if output_folders_reg and len(output_folders_reg) not in (1, n_reg):
        logger.warning(f"[Output] Numero cartelle registri ({len(output_folders_reg)}) diverso dal numero di registri ({n_reg})")
    for idx, record in enumerate(records):
        try:
            # Ignora sempre il campo 'output' già presente nei record: la cartella viene decisa qui
            modalita = str(record.get("modalita", "")).strip().upper()
            url = record.get("url")
            nome_file = record.get("nome_file", "documento")

            # Seleziona cartella di output robusta
            if modalita == "D":
                if output_folders_doc:
                    if len(output_folders_doc) == 1:
                        out_dir = output_folders_doc[0]
                    elif doc_counter < len(output_folders_doc):
                        out_dir = output_folders_doc[doc_counter]
                    else:
                        out_dir = output_folders_doc[-1]
                    doc_counter += 1
                else:
                    out_dir = output_folder
            elif modalita == "R":
                if output_folders_reg:
                    if len(output_folders_reg) == 1:
                        out_dir = output_folders_reg[0]
                    elif reg_counter < len(output_folders_reg):
                        out_dir = output_folders_reg[reg_counter]
                    else:
                        out_dir = output_folders_reg[-1]
                    reg_counter += 1
                else:
                    out_dir = output_folder
            else:
                raise ValueError(f"Modalità non riconosciuta: {modalita}")

            # Forza la cartella di output anche nel record (per compatibilità, ma non usata per la logica)
            record["output"] = out_dir

            logger.info(f"[Output] Record {idx+1}/{len(records)} tipo={modalita} nome={nome_file} -> cartella: {out_dir}")
            # ...existing code...
            # Esegui elaborazione con classe Elaborazione
            elab = Elaborazione(modalita.lower(), url, out_dir, glossario_data, lingua)
            elab.set_nome_file(nome_file)
            success = elab.run(formats=formats)

            # Aggiorna dialog di progresso (se presente)
            try:
                if progress:
                    progress.update(current=idx+1, name=nome_file)
                    # Forza il refresh della GUI
                    if qcore:
                        try:
                            qcore.processEvents()
                        except Exception:
                            pass
                    if getattr(progress, 'cancelled', False):
                        logger.info("[Progress] Elaborazione annullata dall'utente")
                        risultati.append({
                            "file": nome_file,
                            "modalita": modalita,
                            "output": out_dir,
                            "status": "CANCELLED"
                        })
                        break
            except Exception:
                pass

            # Dettaglio tile mancanti
            tiles_missing = []
            if hasattr(elab, 'tiles_missing') and elab.tiles_missing:
                tiles_missing = elab.tiles_missing
            if hasattr(elab, 'tiles_missing_all') and elab.tiles_missing_all:
                tiles_missing = elab.tiles_missing_all

            if success and not tiles_missing:
                risultati.append({
                    "file": nome_file,
                    "modalita": modalita,
                    "output": out_dir,
                    "formati": formats,
                    "status": "SUCCESS"
                })
            elif success and tiles_missing:
                risultati.append({
                    "file": nome_file,
                    "modalita": modalita,
                    "output": out_dir,
                    "formati": formats,
                    "status": "INCOMPLETE",
                    "tiles_missing": tiles_missing
                })
            else:
                risultati.append({
                    "file": nome_file,
                    "modalita": modalita,
                    "output": out_dir,
                    "status": "FAILED",
                    "tiles_missing": tiles_missing if tiles_missing else None
                })

        except Exception as e:
            logger.error(f"[Error] Errore elaborazione record {nome_file}: {e}", exc_info=True)
            risultati.append({
                "file": record.get("nome_file", "sconosciuto"),
                "modalita": modalita,
                "errore": str(e),
                "status": "ERROR"
            })

    # Chiudi la ProgressDialog prima di restituire i risultati
    if progress:
        try:
            progress.close()
        except Exception:
            pass

    logger.info("Operazione completata")
    return risultati
