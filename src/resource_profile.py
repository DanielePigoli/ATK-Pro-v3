"""Profili risorse interni per modulare parallelismo e picchi RAM."""

from __future__ import annotations

import os

RESOURCE_PROFILE_LIGHT = "leggero"
RESOURCE_PROFILE_BALANCED = "bilanciato"
RESOURCE_PROFILE_FAST = "veloce"

DEFAULT_RESOURCE_PROFILE = RESOURCE_PROFILE_BALANCED

RESOURCE_PROFILES = (
    RESOURCE_PROFILE_LIGHT,
    RESOURCE_PROFILE_BALANCED,
    RESOURCE_PROFILE_FAST,
)

RESOURCE_PROFILE_DESCRIPTION_KEYS = {
    RESOURCE_PROFILE_LIGHT: (
        "Usa meno risorse del computer. Consigliato per PC meno potenti o per elaborazioni molto lunghe."
    ),
    RESOURCE_PROFILE_BALANCED: (
        "Compromesso tra velocita e stabilita. Consigliato per la maggior parte dei casi."
    ),
    RESOURCE_PROFILE_FAST: (
        "Prova a completare prima l'elaborazione usando piu risorse. Consigliato solo su PC sufficientemente prestanti."
    ),
}


def normalize_resource_profile(profile: str | None) -> str:
    """Normalizza il profilo richiesto, con fallback prudente al bilanciato."""
    value = (profile or "").strip().lower()
    if value in RESOURCE_PROFILES:
        return value
    return DEFAULT_RESOURCE_PROFILE


def get_resource_profile_description_key(profile: str | None) -> str:
    """Restituisce la chiave glossario descrittiva per il profilo risorse."""
    selected = normalize_resource_profile(profile)
    return RESOURCE_PROFILE_DESCRIPTION_KEYS[selected]


def get_canvas_max_workers(
    profile: str | None = None,
    *,
    cpu_count: int | None = None,
    portal_max_workers: int | None = None,
) -> int:
    """Restituisce il parallelismo canvas rispettando portale e profilo risorse."""
    if portal_max_workers == 1:
        return 1

    available_cpus = cpu_count or os.cpu_count() or 4
    selected = normalize_resource_profile(profile)

    if selected == RESOURCE_PROFILE_LIGHT:
        return min(4, max(1, available_cpus // 3))
    if selected == RESOURCE_PROFILE_FAST:
        return min(12, max(2, (available_cpus * 3) // 4))
    return min(8, max(2, available_cpus // 2))


def get_pdf_open_max_workers(
    total_images: int,
    profile: str | None = None,
    *,
    cpu_count: int | None = None,
) -> int:
    """Restituisce il parallelismo PDF in base al profilo risorse."""
    if total_images <= 1:
        return 1

    available_cpus = cpu_count or os.cpu_count() or 4
    selected = normalize_resource_profile(profile)

    if selected == RESOURCE_PROFILE_LIGHT:
        return min(2, max(1, available_cpus // 3), total_images)
    if selected == RESOURCE_PROFILE_FAST:
        return min(6, max(2, (available_cpus * 3) // 4), total_images)
    return min(4, max(2, available_cpus // 2), total_images)


def get_tile_download_max_workers(
    profile: str | None = None,
    *,
    cpu_count: int | None = None,
    portal_max_workers: int | None = None,
) -> int:
    """Restituisce il parallelismo tile rispettando portale e profilo risorse."""
    if portal_max_workers == 1:
        return 1

    available_cpus = cpu_count or os.cpu_count() or 4
    selected = normalize_resource_profile(profile)

    if selected == RESOURCE_PROFILE_LIGHT:
        return min(4, max(1, available_cpus // 4))
    if selected == RESOURCE_PROFILE_FAST:
        return min(10, max(2, (available_cpus * 3) // 4))
    return min(8, max(2, available_cpus // 2))
