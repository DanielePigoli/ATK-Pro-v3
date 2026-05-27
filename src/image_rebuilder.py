# -*- coding: utf-8 -*-
"""
image_rebuilder.py — ATK-Pro v2.0 (adeguamento logica v1.4.1)
Ricostruisce l'immagine finale dai tiles scaricati.
"""

import os
from logging.handlers import RotatingFileHandler
ATKPRO_ENV = os.environ.get("ATKPRO_ENV", "development").lower()
import logging
from PIL import Image, ImageDraw, ImageFont
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

def rebuild_image(info, tile_dir, source_url=None, update_status=None, update_progress=None, on_error=None):
    """
    Ricostruisce l'immagine finale a partire dai tiles scaricati.
    - info: dict con width, height, tiles[0]["width"]
    - tile_dir: cartella contenente i tile scaricati
    - source_url: URL opzionale da inserire nel footer
    """
    try:
        width = info["width"]
        height = info["height"]
        tile_w = info["tiles"][0]["width"]
        tile_h = info["tiles"][0].get("height", tile_w)  # tile rettangolari (AID §th)
        tile_size = tile_w  # mantenuto per paste coordinates

        # --- FOOTER LOGIC ---
        footer_height = 60 if source_url else 0
        final_image = Image.new("RGB", (width, height + footer_height), (255, 255, 255))
        cols = (width + tile_w - 1) // tile_w
        rows = (height + tile_h - 1) // tile_h
        total = cols * rows
        done = 0

        for y in range(rows):
            for x in range(cols):
                # Support both naming conventions: scaled coords and simple grid coords
                scaled_name = os.path.join(tile_dir, f"tile_{x*tile_size}_{y*tile_size}.jpg")
                simple_name = os.path.join(tile_dir, f"tile_{x}_{y}.jpg")

                if os.path.exists(scaled_name):
                    tile_filename = scaled_name
                elif os.path.exists(simple_name):
                    tile_filename = simple_name
                else:
                    # Neither naming convention present: log and continue
                    logger.warning("Tile mancante: %s", scaled_name)
                    print(f"Tile mancante: {scaled_name}")
                    done += 1
                    if update_progress:
                        try:
                            progress = min(1.0, max(0.0, done / float(total)))
                            update_progress(progress)
                        except Exception:
                            pass
                    continue

                try:
                    tile = Image.open(tile_filename)
                    # Validazione dimensioni tile (solo se l'oggetto ha .size)
                    if hasattr(tile, 'size'):
                        if tile.size[0] <= 1 or tile.size[1] <= 1:
                            logger.warning("Tile corrotto o troppo piccolo: %s", tile_filename)
                            print(f"Tile corrotto o troppo piccolo: {tile_filename}")
                            continue
                    final_image.paste(tile, (x * tile_w, y * tile_h))
                except Exception as e:
                    logger.error("Errore con il tile %s: %s", tile_filename, e)
                    print(f"Errore con il tile {tile_filename}: {e}")
                    if on_error:
                        on_error(f"Errore con il tile {tile_filename}: {e}")

                done += 1
                if update_progress:
                    try:
                        progress = min(1.0, max(0.0, done / float(total)))
                        update_progress(progress)
                    except Exception:
                        pass

        # Disegna footer
        if source_url:
            draw = ImageDraw.Draw(final_image)
            font = None
            font_paths = [
                "arial.ttf", "Arial.ttf", 
                "/System/Library/Fonts/Supplemental/Arial.ttf",
                "/Library/Fonts/Arial.ttf",
                "/System/Library/Fonts/Helvetica.ttc",
                "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"
            ]
            for fpath in font_paths:
                try:
                    font = ImageFont.truetype(fpath, 35)
                    break
                except:
                    continue
            if not font:
                font = ImageFont.load_default()
            draw.text((20, height + 10), f"Source: {source_url}", fill=(0, 0, 0), font=font)

        logger.info("[OK] Immagine ricostruita correttamente dai tiles.")
        if update_status:
            update_status("[OK] Immagine ricostruita correttamente dai tiles.")
        return final_image

    except Exception as e:
        logger.error("Errore nella ricostruzione immagine: %s", e, exc_info=True)
        if on_error:
            on_error(f"Errore nella ricostruzione immagine: {e}")
        return None
