# -*- coding: utf-8 -*-
"""
pdf_utils.py — ATK-Pro v2.0 (ripristino logica v1.4.1 con innesti Qt)
- Generazione PDF da immagini con DPI uniforme.
- Chiusura sistematica delle immagini dopo l'uso.
- Logging chiaro e distinto (nessuna immagine valida, errore di generazione, metadati impostati).
- Costruzione metadati PDF coerente (Title, Author, Subject, Keywords, Creator, Producer).
- Arricchimento PDF esistente con metadati genealogici e tecnici.
- Innesti Qt: update_status(str), update_progress(float 0..1), on_error(str).
"""

import os
import json
import logging
import threading
from logging.handlers import RotatingFileHandler
try:
    from atk_version import PACKAGE_VERSION
except ImportError:
    from src.atk_version import PACKAGE_VERSION
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

from PIL import Image
from pypdf import PdfReader, PdfWriter
try:
    from resource_profile import get_pdf_open_max_workers
except ImportError:
    from src.resource_profile import get_pdf_open_max_workers

def open_image_safe(path):
    """Apre un'immagine in modo sicuro, normalizzando la modalità."""
    try:
        im = Image.open(path)
        return normalize_image_mode(im)
    except Exception as e:
        logger.warning("Immagine non apribile: %s (%s)", path, e)
        return None


def normalize_image_mode(im):
    """Normalizza la modalità immagine (RGB/L)."""
    if im.mode in ("RGBA", "P"):
        return im.convert("RGB")
    elif im.mode == "LA":
        return im.convert("L")
    elif im.mode not in ("RGB", "L", "1"):
        return im.convert("RGB")
    return im


def _pdf_open_max_workers(
    total_images: int,
    cpu_count: int | None = None,
    resource_profile: str | None = None,
) -> int:
    """Limita l'apertura parallela delle immagini per contenere i picchi RAM."""
    return get_pdf_open_max_workers(
        total_images,
        resource_profile,
        cpu_count=cpu_count,
    )


def _pdf_progress_path(output_pdf_path: str) -> str:
    return output_pdf_path + ".progress.json"


def _save_pdf_progress(output_pdf_path: str, payload: dict) -> None:
    progress_path = _pdf_progress_path(output_pdf_path)
    tmp_path = progress_path + ".tmp"
    with open(tmp_path, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=2)
    os.replace(tmp_path, progress_path)


def _clear_pdf_progress(output_pdf_path: str) -> None:
    progress_path = _pdf_progress_path(output_pdf_path)
    try:
        if os.path.exists(progress_path):
            os.remove(progress_path)
    except Exception as exc:
        logger.warning("Impossibile pulire il checkpoint PDF: %s", exc)


def create_pdf_from_images(image_paths, output_pdf_path, resolution_dpi=400,
                            update_status=None, update_progress=None, on_error=None,
                            resource_profile: str | None = None):
    """
    Crea un PDF a partire da una lista di immagini.
    Restituisce il percorso del PDF creato, oppure None in caso di errore.
    """
    if not image_paths:
        logger.warning("Nessuna immagine valida per il PDF.")
        if on_error:
            on_error("Nessuna immagine valida per il PDF.")
        return None

    import concurrent.futures
    logger.info("[PDF] Preparo le pagine del PDF (parallelizzato)...")
    images = []
    total = len(image_paths)
    done = 0
    valid_paths: list[str | None] = [None] * total
    progress_lock = threading.Lock()
    progress_state = {
        "status": "preparing_images",
        "output_pdf_path": output_pdf_path,
        "total_requested": total,
        "prepared_images": 0,
        "valid_image_paths": [],
    }
    _save_pdf_progress(output_pdf_path, progress_state)

    def _open_and_progress(item):
        index, path = item
        im = open_image_safe(path)
        nonlocal done
        with progress_lock:
            done += 1
            if im:
                valid_paths[index] = path
            ordered_valid_paths = [p for p in valid_paths if p]
            progress_state["prepared_images"] = len(ordered_valid_paths)
            progress_state["valid_image_paths"] = ordered_valid_paths
            _save_pdf_progress(output_pdf_path, progress_state)
        if update_progress:
            try:
                progress = min(1.0, max(0.0, done / float(total)))
                update_progress(progress)
            except Exception:
                pass
        return im

    # L'apertura immagini può generare picchi RAM; resta parallela ma con cap prudente.
    try:
        max_workers = _pdf_open_max_workers(total, resource_profile=resource_profile)
    except Exception:
        max_workers = min(4, total)
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        results = list(executor.map(_open_and_progress, enumerate(image_paths)))
    images = [im for im in results if im]

    if not images:
        logger.error("Nessuna pagina valida per il PDF.")
        if on_error:
            on_error("Nessuna pagina valida per il PDF.")
        return None

    try:
        first, rest = images[0], images[1:]
        logger.info(f"[PDF] Generazione PDF: {output_pdf_path}")
        progress_state["status"] = "writing_pdf"
        _save_pdf_progress(output_pdf_path, progress_state)
        first.save(output_pdf_path, "PDF", save_all=True, append_images=rest,
                   resolution=resolution_dpi)
        logger.info(f"[OK] PDF creato: {output_pdf_path}")
        _clear_pdf_progress(output_pdf_path)
        if update_status:
            update_status(f"PDF creato: {output_pdf_path}")
        return output_pdf_path
    except Exception as e:
        logger.error("Errore nella generazione PDF: %s", e, exc_info=True)
        if on_error:
            on_error(f"Errore nella generazione PDF: {e}")
        return None
    finally:
        for im in images:
            try:
                im.close()
            except Exception:
                pass


def build_metadata_dict(title, subject, ua, ark):
    """Costruisce il dizionario dei metadati PDF."""
    keywords = ", ".join([s for s in [ua, ark, title] if s])
    return {
        "/Title": str(title or ""),
        "/Author": "Portale Antenati",
        "/Subject": str(subject or ""),
        "/Keywords": keywords,
        "/Creator": "Antenati ToolKit Pro",
        "/Producer": f"Antenati ToolKit Pro v{PACKAGE_VERSION}",
    }


def enrich_pdf_metadata(pdf_path: str, title: str, subject: str,
                        ua: str | None, ark: str | None,
                        update_status=None, on_error=None):
    """
    Arricchisce un PDF esistente con metadati genealogici e tecnici.
    Restituisce True se completato, False in caso di errore.
    """
    if not os.path.exists(pdf_path):
        logger.error("PDF non trovato: %s", pdf_path)
        if on_error:
            on_error(f"PDF non trovato: {pdf_path}")
        return False

    try:
        reader = PdfReader(pdf_path)
        writer = PdfWriter()
        for page in reader.pages:
            writer.add_page(page)

        metadata = build_metadata_dict(title, subject, ua, ark)
        writer.add_metadata(metadata)

        tmp = pdf_path + ".tmp"
        with open(tmp, "wb") as f:
            writer.write(f)
        os.replace(tmp, pdf_path)

        logger.info("[OK] Metadati PDF impostati.")
        if update_status:
            update_status("Metadati PDF impostati.")
        return True
    except Exception as e:
        logger.error("Impossibile arricchire i metadati del PDF: %s", e, exc_info=True)
        if on_error:
            on_error(f"Impossibile arricchire i metadati del PDF: {e}")
        return False
