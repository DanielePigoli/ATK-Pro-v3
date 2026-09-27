import json
import logging
import os
import shutil
import sys
import tempfile

_is_frozen = getattr(sys, 'frozen', False)
if _is_frozen:
    BASE_DIR = sys._MEIPASS
else:
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

_EXE_DIR = os.path.dirname(sys.executable) if _is_frozen else BASE_DIR
_PORTABLE_SENTINEL = os.path.join(_EXE_DIR, "portable.txt")
IS_PORTABLE = os.path.exists(_PORTABLE_SENTINEL)

def _config_file_path():
    """Ritorna il percorso del file di configurazione utente."""
    if IS_PORTABLE:
        return os.path.join(_EXE_DIR, "config.json")
    return os.path.join(os.path.expanduser("~"), ".config", "atk-pro", "config.json")


def _next_corrupt_backup_path(config_path: str) -> str:
    """Restituisce un nome libero senza sovrascrivere precedenti recuperi."""
    candidate = f"{config_path}.corrupt"
    suffix = 1
    while os.path.exists(candidate):
        candidate = f"{config_path}.corrupt.{suffix}"
        suffix += 1
    return candidate


def _load_config_object(config_path: str) -> dict:
    """Carica un config JSON valido, considerando corrotte le radici non-oggetto."""
    with open(config_path, encoding="utf-8") as fh:
        data = json.load(fh)
    if not isinstance(data, dict):
        raise ValueError("La radice del file di configurazione deve essere un oggetto JSON")
    return data


def _atomic_write_config(config_path: str, data: dict) -> None:
    """Scrive JSON nella stessa directory e lo pubblica con sostituzione atomica."""
    config_dir = os.path.dirname(config_path) or os.curdir
    os.makedirs(config_dir, exist_ok=True)
    temp_path = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            newline="\n",
            prefix=f".{os.path.basename(config_path)}.",
            suffix=".tmp",
            dir=config_dir,
            delete=False,
        ) as fh:
            temp_path = fh.name
            json.dump(data, fh, ensure_ascii=False, indent=2)
            fh.write("\n")
            fh.flush()
            os.fsync(fh.fileno())
        os.replace(temp_path, config_path)
        temp_path = None
    finally:
        if temp_path and os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except OSError:
                pass


def _update_config_file(config_path: str, updates: dict) -> str | None:
    """Aggiorna il config preservando chiavi esistenti e recuperando JSON corrotti.

    Restituisce il percorso dell'eventuale copia di sicurezza creata. Errori di
    accesso o scrittura vengono propagati, cosi' il chiamante puo' registrarli
    senza considerare persistito un aggiornamento fallito.
    """
    if not isinstance(updates, dict):
        raise TypeError("Gli aggiornamenti della configurazione devono essere un dizionario")

    data = {}
    backup_path = None
    if os.path.exists(config_path):
        try:
            data = _load_config_object(config_path)
        except (json.JSONDecodeError, UnicodeDecodeError, ValueError):
            backup_path = _next_corrupt_backup_path(config_path)
            shutil.copy2(config_path, backup_path)
            logging.warning(
                "Configurazione non valida preservata in %s; ricostruzione del file in corso",
                backup_path,
            )

    data.update(updates)
    _atomic_write_config(config_path, data)
    return backup_path


def _write_config_prefs(key: str, value) -> bool:
    """Aggiorna una preferenza nel config JSON senza rischiare file parziali."""
    try:
        _update_config_file(_config_file_path(), {key: value})
        return True
    except Exception as exc:
        logging.warning("Impossibile salvare la preferenza %s: %s", key, exc)
        return False
