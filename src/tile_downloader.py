# -*- coding: utf-8 -*-
"""
tile_downloader.py — ATK-Pro v2.0 (adeguamento logica v1.4.1)
Scarica tutti i tiles IIIF di un canvas e restituisce la lista completa.
"""

import os
import time
import logging
import requests
from urllib.parse import urlparse

try:
    from portal_registry import get_portal_tile_download_policy
except ImportError:  # pragma: no cover - package import path
    from src.portal_registry import get_portal_tile_download_policy

logger = logging.getLogger(__name__)

MAX_RETRIES = 3

HEADERS_UX = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/115.0.0.0 Safari/537.36"
    ),
    "Accept": "image/avif,image/webp,image/apng,image/*,*/*;q=0.8",
    "Accept-Language": "it-IT,it;q=0.9",
    "Referer": "https://antenati.cultura.gov.it/",
    "Origin": "https://antenati.cultura.gov.it",
    "Connection": "keep-alive",
}


def _origin_from_url(url):
    try:
        parsed = urlparse(url)
        if parsed.scheme and parsed.netloc:
            return f"{parsed.scheme}://{parsed.netloc}"
    except Exception:
        return None
    return None


def _headers_for_tile_url(url, referer=None):
    headers = dict(HEADERS_UX)
    if referer:
        origin = referer.rstrip("/")
        headers["Referer"] = origin + "/"
        headers["Origin"] = origin
        return headers
    if "dam-antenati.cultura.gov.it" in url:
        return headers
    origin = _origin_from_url(url)
    if origin:
        headers["Referer"] = origin + "/"
        headers.pop("Origin", None)
    return headers


def _remove_partial_tile(filename):
    try:
        if os.path.exists(filename):
            os.remove(filename)
    except OSError:
        logger.debug("Impossibile rimuovere tile parziale: %s", filename, exc_info=True)


def _stream_response_to_file(response, filename):
    tmp_filename = f"{filename}.part"
    _remove_partial_tile(tmp_filename)
    with open(tmp_filename, "wb") as f:
        for chunk in response.iter_content(8192):
            if chunk:
                f.write(chunk)
    os.replace(tmp_filename, filename)

def download_tile(url, x, y, tile_size, output_dir, quality="default", img_width=None, img_height=None, inter_delay=0.0, referer=None, size_keyword="full"):
    """Scarica un singolo tile IIIF e lo salva nella cartella di output."""
    # x,y possono arrivare come offset in pixel oppure come indici di col/row.
    # Se sono indici (es. 0,1) li moltiplichiamo per ottenere gli offset in pixel.
    if isinstance(x, int) and isinstance(y, int) and x < tile_size and y < tile_size:
        col = int(x)
        row = int(y)
        pixel_x = col * tile_size
        pixel_y = row * tile_size
    else:
        pixel_x = x
        pixel_y = y
        col = int(pixel_x // tile_size)
        row = int(pixel_y // tile_size)

    # Calcola le dimensioni reali del tile (tile di bordo possono essere più piccoli)
    region_w = min(tile_size, img_width - pixel_x) if img_width is not None else tile_size
    region_h = min(tile_size, img_height - pixel_y) if img_height is not None else tile_size
    region_w = max(1, region_w)
    region_h = max(1, region_h)

    # Soglia minima proporzionale all'area del tile (tile di bordo possono essere < 1024 byte)
    min_file_size = max(16, (region_w * region_h) // 128)

    filename = os.path.join(output_dir, f"tile_{col}_{row}.jpg")
    url_tile = f"{url}/{pixel_x},{pixel_y},{region_w},{region_h}/{size_keyword}/0/{quality}.jpg"

    # Tile già presente e valido
    if os.path.exists(filename) and os.path.getsize(filename) >= min_file_size:
        logger.info("Tile già presente e valido: %s", filename)
        return filename

    # Ciclo di retry con backoff crescente
    for attempt in range(1, MAX_RETRIES + 1):
        if attempt == 1 and inter_delay > 0:
            time.sleep(inter_delay)  # delay tra richieste per portali con rate-limiting (es. Heidelberg)
        elif attempt > 1:
            time.sleep(5 * (attempt - 1) if inter_delay > 0 else 2 * (attempt - 1))  # backoff: 5s/10s Heidelberg, 2s/4s altri
        logger.info("[Tile] Scarico tile (tentativo %d/%d) da URL: %s", attempt, MAX_RETRIES, url_tile)
        try:
            response = requests.get(url_tile, headers=_headers_for_tile_url(url_tile, referer=referer), stream=True, timeout=30)
        except Exception as e:
            logger.warning("Tentativo %d fallito per %s: %s", attempt, url_tile, e)
            continue

        if response.status_code == 200:
            try:
                _stream_response_to_file(response, filename)
            except (requests.exceptions.ChunkedEncodingError, requests.exceptions.ConnectionError, OSError) as e:
                _remove_partial_tile(filename)
                _remove_partial_tile(f"{filename}.part")
                logger.warning("Tentativo %d interrotto durante lo stream per %s: %s", attempt, url_tile, e)
                continue
            # Controllo dimensione minima proporzionale
            if os.path.getsize(filename) < min_file_size:
                logger.warning("[Warning] Tile troppo piccolo (%d byte, min=%d): %s",
                               os.path.getsize(filename), min_file_size, filename)
                os.remove(filename)
                continue
            logger.info("[OK] Tile salvato correttamente: %s", filename)
            return filename
        elif response.status_code == 404:
            # Fallback .png: alcuni portali IIIF servono PNG invece di JPEG.
            # Salviamo nel filename .jpg standard: Pillow legge dal contenuto, non dall'estensione.
            url_tile_png = f"{url}/{pixel_x},{pixel_y},{region_w},{region_h}/{size_keyword}/0/{quality}.png"
            logger.debug("Tile .jpg non trovato (404), provo .png: %s", url_tile_png)
            try:
                resp_png = requests.get(url_tile_png, headers=_headers_for_tile_url(url_tile_png, referer=referer), stream=True, timeout=30)
                if resp_png.status_code == 200:
                    _stream_response_to_file(resp_png, filename)
                    if os.path.getsize(filename) >= min_file_size:
                        logger.info("[OK] Tile .png salvato come %s", filename)
                        return filename
                    else:
                        os.remove(filename)
            except Exception as e:
                logger.debug("Fallback .png fallito per %s: %s", url_tile_png, e)
            return None
        else:
            logger.error("[Error] Errore HTTP %s per %s", response.status_code, url_tile)
            continue

    logger.error("[Error] Tutti i tentativi di download falliti per %s", url_tile)
    return None

def download_tiles(infojson, output_dir, update_progress=None, portale=None, referer=None):
    """Scarica tutti i tile definiti in un info.json IIIF e restituisce la lista completa."""
    import concurrent.futures
    base_url = infojson.get("@id") or infojson.get("id") or infojson.get("@context", "")
    width = infojson["width"]
    height = infojson["height"]
    # IIIF Image API v1.1 (es. Gallica BnF) non ha il campo "tiles"; usa tile 512px e quality "native"
    if "tiles" in infojson:
        tile_w = infojson["tiles"][0]["width"]
        tile_h = infojson["tiles"][0].get("height", tile_w)
        quality = "default"
    else:
        tile_w = 512
        tile_h = 512
        profile = infojson.get("profile", "")
        quality = "native" if (isinstance(profile, str) and "1.1" in profile) else "default"
    tile_size = tile_w  # mantenuto per compatibilità con download_tile()
    context = infojson.get("@context") or infojson.get("context") or ""
    image_type = infojson.get("type") or infojson.get("@type") or ""
    profile_text = str(infojson.get("profile", ""))
    is_image_api_v3 = (
        image_type == "ImageService3"
        or "image/3" in str(context)
        or "image/3" in profile_text
    )
    size_keyword = "max" if is_image_api_v3 else "full"

    cols = (width + tile_w - 1) // tile_w
    rows = (height + tile_h - 1) // tile_h
    total = cols * rows
    logger.info("Inizio download di %d x %d tiles (tile_size=%d)", cols, rows, tile_size)
    os.makedirs(output_dir, exist_ok=True)

    def expected_tile_filename(x, y):
        col = int(x)
        row = int(y)
        return os.path.join(output_dir, f"tile_{col}_{row}.jpg")

    expected_files = [expected_tile_filename(x, y) for y in range(rows) for x in range(cols)]

    max_global_retries = 3
    # Parallelizzazione automatica: usa metà dei core disponibili, minimo 2, massimo 8.
    # Eventuali limiti per portale arrivano dalla registry centrale.
    try:
        cpu_count = os.cpu_count() or 4
        default_max_workers = min(8, max(2, cpu_count // 2))
    except Exception:
        default_max_workers = 4
    portal_max_workers, inter_delay = get_portal_tile_download_policy(portale)
    max_workers = portal_max_workers or default_max_workers
    def _tile_call_args(x, y):
        base_args = (base_url, x, y, tile_size, output_dir, quality, width, height, inter_delay)
        if referer is not None or size_keyword != "full":
            return base_args + (referer, size_keyword)
        return base_args

    tile_args = [_tile_call_args(x, y) for y in range(rows) for x in range(cols)]
    attempt = 0
    tiles_downloaded = set()
    missing_files = set(expected_files)
    done = 0

    while attempt < max_global_retries and missing_files:
        logger.info(f"[Tiles] Tentativo globale {attempt+1}/{max_global_retries}. Tiles da scaricare: {len(missing_files)}")
        args_to_download = []
        for idx, (x, y) in enumerate([(x, y) for y in range(rows) for x in range(cols)]):
            fname = expected_tile_filename(x, y)
            if fname in missing_files:
                args_to_download.append(_tile_call_args(x, y))

        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_tile = {executor.submit(download_tile, *args): args for args in args_to_download}
            for future in concurrent.futures.as_completed(future_to_tile):
                result = future.result()
                done += 1
                if result:
                    tiles_downloaded.add(result)
                    missing_files.discard(result)
                if update_progress:
                    try:
                        progress = min(1.0, max(0.0, done / float(total * max_global_retries)))
                        update_progress(progress)
                    except Exception:
                        pass
        # Dopo ogni ciclo, aggiorna missing_files (soglia minima proporzionale per tile di bordo)
        def _is_valid(f, x, y):
            if not os.path.exists(f):
                return False
            rw = min(tile_size, width - x * tile_size)
            rh = min(tile_size, height - y * tile_size)
            return os.path.getsize(f) >= max(16, (rw * rh) // 128)
        missing_files = set(
            expected_tile_filename(x, y)
            for y in range(rows) for x in range(cols)
            if not _is_valid(expected_tile_filename(x, y), x, y)
        )
        attempt += 1

    if missing_files:
        logger.warning(f"[Tiles] ATTENZIONE: {len(missing_files)} tile NON scaricati dopo {max_global_retries} tentativi.")
        for mf in sorted(missing_files):
            logger.warning(f"[Tiles] Mancante: {mf}")
    else:
        logger.info("[Tiles] Tutti i tile scaricati correttamente.")

    logger.info("[Tiles] Download completato di %d/%d scaricati", len(tiles_downloaded), total)
    return list(tiles_downloaded), list(missing_files)
