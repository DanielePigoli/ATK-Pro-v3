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
import logging
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


def create_pdf_from_images(image_paths, output_pdf_path, resolution_dpi=400,
                           update_status=None, update_progress=None, on_error=None):
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
    def _open_and_progress(path):
        im = open_image_safe(path)
        nonlocal done
        done += 1
        if update_progress:
            try:
                progress = min(1.0, max(0.0, done / float(total)))
                update_progress(progress)
            except Exception:
                pass
        return im

    # Parallelizzazione automatica: usa metà dei core disponibili, minimo 2, massimo 8
    import os
    try:
        cpu_count = os.cpu_count() or 4
        max_workers = min(8, max(2, cpu_count // 2))
    except Exception:
        max_workers = 4
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        results = list(executor.map(_open_and_progress, image_paths))
    images = [im for im in results if im]

    if not images:
        logger.error("Nessuna pagina valida per il PDF.")
        if on_error:
            on_error("Nessuna pagina valida per il PDF.")
        return None

    try:
        first, rest = images[0], images[1:]
        logger.info(f"[PDF] Generazione PDF: {output_pdf_path}")
        first.save(output_pdf_path, "PDF", save_all=True, append_images=rest,
                   resolution=resolution_dpi)
        logger.info(f"[OK] PDF creato: {output_pdf_path}")
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
