from src.resource_profile import (
    DEFAULT_RESOURCE_PROFILE,
    RESOURCE_PROFILE_BALANCED,
    RESOURCE_PROFILE_DESCRIPTION_KEYS,
    RESOURCE_PROFILE_FAST,
    RESOURCE_PROFILE_LIGHT,
    get_canvas_max_workers,
    get_pdf_open_max_workers,
    get_resource_profile_description_key,
    normalize_resource_profile,
)


def test_normalize_resource_profile_defaults_to_balanced():
    assert normalize_resource_profile(None) == DEFAULT_RESOURCE_PROFILE
    assert normalize_resource_profile("") == DEFAULT_RESOURCE_PROFILE
    assert normalize_resource_profile("sconosciuto") == DEFAULT_RESOURCE_PROFILE


def test_normalize_resource_profile_accepts_known_values():
    assert normalize_resource_profile("leggero") == RESOURCE_PROFILE_LIGHT
    assert normalize_resource_profile("BILANCIATO") == RESOURCE_PROFILE_BALANCED
    assert normalize_resource_profile(" veloce ") == RESOURCE_PROFILE_FAST


def test_description_key_follows_normalized_profile():
    assert get_resource_profile_description_key("leggero") == RESOURCE_PROFILE_DESCRIPTION_KEYS[RESOURCE_PROFILE_LIGHT]
    assert get_resource_profile_description_key("BILANCIATO") == RESOURCE_PROFILE_DESCRIPTION_KEYS[RESOURCE_PROFILE_BALANCED]
    assert get_resource_profile_description_key("sconosciuto") == RESOURCE_PROFILE_DESCRIPTION_KEYS[RESOURCE_PROFILE_BALANCED]


def test_canvas_workers_respect_profile_progression():
    light = get_canvas_max_workers(RESOURCE_PROFILE_LIGHT, cpu_count=16)
    balanced = get_canvas_max_workers(RESOURCE_PROFILE_BALANCED, cpu_count=16)
    fast = get_canvas_max_workers(RESOURCE_PROFILE_FAST, cpu_count=16)
    assert light == 4
    assert balanced == 8
    assert fast == 12


def test_canvas_workers_keep_prudent_portals_sequential():
    assert get_canvas_max_workers(RESOURCE_PROFILE_FAST, cpu_count=16, portal_max_workers=1) == 1
    assert get_canvas_max_workers(RESOURCE_PROFILE_LIGHT, cpu_count=16, portal_max_workers=1) == 1


def test_pdf_workers_respect_profile_progression():
    light = get_pdf_open_max_workers(20, RESOURCE_PROFILE_LIGHT, cpu_count=16)
    balanced = get_pdf_open_max_workers(20, RESOURCE_PROFILE_BALANCED, cpu_count=16)
    fast = get_pdf_open_max_workers(20, RESOURCE_PROFILE_FAST, cpu_count=16)
    assert light == 2
    assert balanced == 4
    assert fast == 6


def test_pdf_workers_stay_bounded_by_total_images():
    assert get_pdf_open_max_workers(1, RESOURCE_PROFILE_FAST, cpu_count=16) == 1
    assert get_pdf_open_max_workers(2, RESOURCE_PROFILE_FAST, cpu_count=16) == 2
