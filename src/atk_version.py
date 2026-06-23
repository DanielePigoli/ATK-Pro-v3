"""Versione applicativa condivisa da GUI, updater e metadati."""

from packaging.version import InvalidVersion, Version


BASE_VERSION = "3.0.0"
RELEASE_STAGE = "rc2"
VERSION = f"{BASE_VERSION}-{RELEASE_STAGE}" if RELEASE_STAGE else BASE_VERSION
DISPLAY_VERSION = f"{BASE_VERSION} {RELEASE_STAGE.upper()}" if RELEASE_STAGE else BASE_VERSION
PACKAGE_VERSION = VERSION


def is_newer_version(candidate: str, current: str = VERSION) -> bool:
    """Confronta versioni PEP 440, includendo correttamente le prerelease."""
    try:
        return Version(candidate) > Version(current)
    except (InvalidVersion, TypeError):
        return False
