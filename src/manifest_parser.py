import requests
import os
import json
import logging
from url_utils import _parse_ark_from_url

logger = logging.getLogger(__name__)

# Intestazioni per simulare un browser reale e superare il 403
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/115.0.0.0 Safari/537.36"
    ),
    "Referer": "https://antenati.cultura.gov.it/",
    "Accept": "application/json",
    "Connection": "keep-alive",
    # Header aggiuntivi per replicare il comportamento del monolite
    "Origin": "https://antenati.cultura.gov.it",
    "Sec-Fetch-Site": "same-origin",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Dest": "empty",
    "Accept-Language": "it-IT,it;q=0.9,en-US;q=0.8,en;q=0.7",
    "Accept-Encoding": "gzip, deflate, br"
}

# RIMOSSO: Mappa hardcoded era SBAGLIATA! Usa sempre il metodo della v1.4.1: estrarre dal HTML della pagina


def build_manifest_url(ark_url: str) -> str:
    """
    Costruisce l'URL del manifest IIIF (fallback se la pagina HTML non è disponibile).
    Nota: il metodo preferito è estrarre dal HTML della pagina di Antenati (come in v1.4.1).
    """
    # Se non è un URL Antenati, non provare a costruire un manifest ARK
    if "antenati.cultura.gov.it" not in ark_url:
        logger.debug(f"[Manifest] Ignoro URL non Antenati in build_manifest_url: {ark_url}")
        # Restituiamo l'URL invariato o solleviamo un errore gestito
        return ark_url

    ark_full = _parse_ark_from_url(ark_url)
    logger.info(f"[Manifest] ark_full = '{ark_full}'")

    # Fallback: mantenere la vecchia logica per altri casi (NO mappa hardcoded!)
    if ark_full:
        parts = ark_full.split('/')
        if len(parts) >= 3:
            ark_base = '/'.join(parts[:3])
        else:
            ark_base = ark_full
        base_url = f"https://antenati.cultura.gov.it/iiif/{ark_base}"

        url_json = f"{base_url}/manifest.json"
        url_noext = f"{base_url}/manifest"

        logger.debug(f"[Manifest] Tentativo HEAD su {url_json}")
        try:
            r = requests.head(url_json, headers=HEADERS, timeout=10)
            logger.debug(f"[Manifest] HEAD {url_json} status {r.status_code}")
            if r.status_code == 200:
                return url_json
        except Exception as e:
            logger.debug(f"[Manifest] HEAD {url_json} eccezione: {e}")

        logger.debug(f"[Manifest] Tentativo HEAD su {url_noext}")
        try:
            r = requests.head(url_noext, headers=HEADERS, timeout=10)
            logger.debug(f"[Manifest] HEAD {url_noext} status {r.status_code}")
            if r.status_code == 200:
                return url_noext
        except Exception as e:
            logger.debug(f"[Manifest] HEAD {url_noext} eccezione: {e}")

        logger.warning(f"[Manifest] Nessun manifest trovato, ritorno fallback {url_json}")
        return url_json
    raise ValueError(f"Impossibile costruire manifest da URL: {ark_url}")

class ManifestBaseParser:
    def __init__(self, ark_url: str):
        self.ark_url = ark_url
        self.manifest = None

    def fetch_manifest(self):
        manifest_url = build_manifest_url(self.ark_url)
        print(f"DEBUG: Tentativo GET manifest da URL: {manifest_url}")
        response = requests.get(manifest_url, headers=HEADERS, timeout=30)
        print(f"DEBUG: Risposta HTTP GET: {response.status_code}")
        response.raise_for_status()
        self.manifest = response.json()
        return self.manifest

    def get_metadata(self):
        if not self.manifest:
            raise RuntimeError("Manifest non caricato")
        return self.manifest.get("metadata", {})

    def parse_tiles(self):
        if not self.manifest:
            raise RuntimeError("Manifest non caricato")
        return self.manifest.get("sequences", [])[0].get("canvases", [])

class ManifestUAParser(ManifestBaseParser):
    # Parser per documenti UA (atti singoli).
    pass

class ManifestUDParser(ManifestBaseParser):
    # Parser per registri UD (atti multipli).
    pass

def get_parser(ark_url: str):
    # Restituisce il parser corretto in base al tipo di record.
    if "ua" in ark_url.lower():
        return ManifestUAParser(ark_url)
    elif "ud" in ark_url.lower():
        return ManifestUDParser(ark_url)
    else:
        return ManifestBaseParser(ark_url)


# ===== Funzione estrai_metadati_da_manifest (dalla v1.4.1 e manifest_parser_old.py) =====

def estrai_metadati_da_manifest(
    manifest_path,
    record_prefix=None,
    record_url=None,
    record_nome_file=None,
    immagini_generate=None
):
    """
    Estrae metadati genealogici e tecnici da un manifest IIIF salvato in locale.
    Salva due file JSON:
    - *_genealogico.json → dati utili per ricerca genealogica, OCR, GEDCOM
    - *_tecnico.json → dati tecnici e strutturali dell'immagine/registro

    Parametri:
    manifest_path: percorso del file manifest IIIF
    record_prefix: primo carattere del record ('D','d','R','r')
    record_url: URL originale del record (necessario per distinguere an_ua / an_ud)
    record_nome_file: descrizione del record, usata per creare cartella dedicata
    immagini_generate: lista di file immagine/PDF associati
    """
    try:
        with open(manifest_path, "r", encoding="utf-8") as f:
            manifest_data = json.load(f)
    except Exception as e:
        logger.error(f"❌ Errore apertura manifest {manifest_path}: {e}")
        try:
            print(f"❌ Errore apertura manifest {manifest_path}: {e}")
        except Exception:
            pass
        return

    # Cartella di output differenziata
    base_name = os.path.splitext(os.path.basename(manifest_path))[0]
    output_dir = os.path.dirname(manifest_path)
    if record_nome_file:
        safe_name = "".join(c for c in record_nome_file if c not in '\\/*?:"<>|').strip()
        output_dir = os.path.join(output_dir, safe_name)
        os.makedirs(output_dir, exist_ok=True)

    genealogico = {}
    tecnico = {}

    try:
        # Titolo
        genealogico["titolo"] = (
            manifest_data.get("label", {}).get("it", [""])[0]
            if isinstance(manifest_data.get("label"), dict)
            else manifest_data.get("label", "")
        )

        # Metadati genealogici vs tecnici
        if "metadata" in manifest_data and isinstance(manifest_data["metadata"], list):
            for meta in manifest_data["metadata"]:
                label = (
                    meta.get("label", {}).get("it", [""])[0]
                    if isinstance(meta.get("label"), dict)
                    else meta.get("label", "")
                )
                value = (
                    meta.get("value", {}).get("it", [""])[0]
                    if isinstance(meta.get("value"), dict)
                    else meta.get("value", "")
                )
                if any(k in label.lower() for k in ["data", "luogo", "atto", "nome", "cognome", "comune", "provincia"]):
                    genealogico[label] = value
                else:
                    tecnico[label] = value

        # --- Gestione Documenti vs Registri ---
        if record_prefix in ["D", "d"]:
            if record_url and "an_ua" in record_url:
                try:
                    suffix = record_url.strip("/").split("/")[-1]
                    tecnico["canvas_target"] = suffix
                    logger.info(f"[OK] Canvas target (an_ua) selezionato: {suffix}")
                except Exception as e:
                    logger.error(f"[Error] Errore estrazione suffisso da URL {record_url}: {e}")
            elif record_url and "an_ud" in record_url:
                try:
                    requested_id = record_url.strip("/").split("/")[-1]
                    
                    # Prova IIIF v3 (items)
                    if "items" in manifest_data and manifest_data["items"]:
                        match = next((c.get("id") for c in manifest_data["items"] if requested_id in c.get("id","")), None)
                        if match:
                            tecnico["canvas_target"] = match
                            logger.info(f"[OK] Canvas target (an_ud, IIIF v3) selezionato: {match}")
                        else:
                            logger.warning(f"[Warning] Nessun canvas corrispondente a {requested_id} negli items")
                    # Prova IIIF v2 (sequences/canvases)
                    elif "sequences" in manifest_data and manifest_data["sequences"]:
                        canvases = manifest_data["sequences"][0].get("canvases", [])
                        match = next((c.get("@id") for c in canvases if requested_id in c.get("@id","")), None)
                        if match:
                            tecnico["canvas_target"] = match
                            logger.info(f"[OK] Canvas target (an_ud, IIIF v2) selezionato: {match}")
                        else:
                            logger.warning(f"[Warning] Nessun canvas corrispondente a {requested_id} nei canvases")
                    else:
                        # Fallback: usa direttamente l'ID estratto dall'URL
                        tecnico["canvas_target"] = requested_id
                        logger.warning(f"[Warning] Nessuna struttura IIIF trovata, uso ID diretto da URL: {requested_id}")
                except Exception as e:
                    logger.error(f"[Error] Errore selezione canvas an_ud da {manifest_path}: {e}")
            else:
                logger.warning(f"[Warning] Documento senza tipo riconosciuto in {manifest_path}")

        elif record_prefix in ["R", "r"]:
            target_canvas_id = manifest_data.get("target_canvas_id")
            if target_canvas_id:
                tecnico["canvas_target"] = target_canvas_id
                logger.info(f"[OK] Canvas target (Registro) selezionato: {target_canvas_id}")
            elif "items" in manifest_data:
                tecnico["numero_canvas"] = len(manifest_data["items"])
                tecnico["canvas_id_list"] = [c.get("id") for c in manifest_data["items"]]
                logger.info(f"[Info] Registro con {tecnico['numero_canvas']} canvas (IIIF v3)")
            elif "sequences" in manifest_data and manifest_data["sequences"]:
                canvases = manifest_data["sequences"][0].get("canvases", [])
                tecnico["numero_canvas"] = len(canvases)
                tecnico["canvas_id_list"] = [c.get("@id") for c in canvases]
                logger.info(f"[Info] Registro con {tecnico['numero_canvas']} canvas (IIIF v2)")
            else:
                logger.error(f"[Error] Nessun canvas selezionabile per Registro in {manifest_path}")

        else:
            # Se non è stato fornito un `record_prefix`, proviamo a inferire se il
            # manifest rappresenta un registro (presenza di `items`) e popolare
            # i metadati tecnici di conseguenza — utile per i test che passano solo il file.
            if "items" in manifest_data:
                tecnico["numero_canvas"] = len(manifest_data["items"])
                tecnico["canvas_id_list"] = [c.get("id") for c in manifest_data["items"]]
                logger.info(f"[Info] Registro (inferred) con {tecnico['numero_canvas']} canvas (IIIF v3)")
            elif "sequences" in manifest_data and manifest_data["sequences"]:
                canvases = manifest_data["sequences"][0].get("canvases", [])
                tecnico["numero_canvas"] = len(canvases)
                tecnico["canvas_id_list"] = [c.get("@id") for c in canvases]
                logger.info(f"[Info] Registro (inferred) con {tecnico['numero_canvas']} canvas (IIIF v2)")

        # Diritti
        if "rights" in manifest_data:
            tecnico["diritti"] = manifest_data["rights"]

        # File associati
        if immagini_generate:
            genealogico["file_associati"] = immagini_generate
            tecnico["file_associati"] = immagini_generate

        # Salvataggio file JSON
        genealogico_path = os.path.join(output_dir, f"{base_name}_genealogico.json")
        tecnico_path = os.path.join(output_dir, f"{base_name}_tecnico.json")

        try:
            with open(genealogico_path, "w", encoding="utf-8") as fg:
                json.dump(genealogico, fg, ensure_ascii=False, indent=2)
            with open(tecnico_path, "w", encoding="utf-8") as ft:
                json.dump(tecnico, ft, ensure_ascii=False, indent=2)
            logger.info(f"[Metadata] Metadati genealogici salvati in: {genealogico_path}")
            logger.info(f"[Metadata] Metadati tecnici salvati in: {tecnico_path}")
            # Stampiamo messaggi leggibili per la CLI e per i test automatici
            try:
                print(f"📄 Metadati genealogici salvati in: {genealogico_path}")
                print(f"📄 Metadati tecnici salvati in: {tecnico_path}")
            except Exception:
                # non critico, proseguiamo
                pass
        except Exception as e:
            logger.error(f"[Error] Errore salvataggio metadati da {manifest_path}: {e}", exc_info=True)
            try:
                print(f"❌ Errore estrazione metadati da {manifest_path}: {e}")
            except Exception:
                pass

    except Exception as e:
        logger.error(f"❌ Errore estrazione metadati da {manifest_path}: {e}", exc_info=True)