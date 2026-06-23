# ATK‑Pro v1.5 – modulo: ui_info
from gettext import gettext as _
try:
    from atk_version import DISPLAY_VERSION
except ImportError:
    from src.atk_version import DISPLAY_VERSION

APP_NAME = _("Antenati ToolKit Pro")
WELCOME_MSG = _(f"Benvenuto in ATK‑Pro v{DISPLAY_VERSION}")
HELP_TEXT = _("Usa la CLI per rigenerare tessere, gestire metadati e creare PDF multipagina.")
