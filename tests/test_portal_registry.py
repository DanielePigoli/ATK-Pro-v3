import src.manifest_utils as manifest_utils
from src.portal_registry import (
    PORTAL_REGISTRY,
    PORTAL_WARNING_MESSAGE_KEYS,
    get_portal,
    get_portal_groups,
    get_portal_referer,
    get_portal_warning_message_key,
    normalize_portal_key,
    portal_keys,
)


def test_registry_has_expected_portal_count_and_unique_keys():
    keys = portal_keys()
    assert len(keys) == 19
    assert len(set(keys)) == len(keys)
    assert set(keys) == set(PORTAL_REGISTRY)


def test_registry_covers_manifest_builders_and_special_portals():
    expected = set(manifest_utils._PORTAL_BUILDERS) | {"antenati", "manifest_diretto"}
    assert set(PORTAL_REGISTRY) == expected


def test_portal_groups_preserve_selector_order():
    groups = get_portal_groups()
    assert groups[0][0] == "\u2500\u2500 Italia \u2500\u2500"
    assert groups[0][1][0] == ("antenati", "Antenati (Cultura.gov.it)")
    assert groups[-1][0] == "\u2500\u2500 Avanzato \u2500\u2500"
    assert groups[-1][1] == (("manifest_diretto", "Manifest diretto (URL gi\u00e0 noto)"),)


def test_normalize_and_lookup_portal_key():
    assert normalize_portal_key("Manifest Diretto") == "manifest_diretto"
    assert normalize_portal_key("internet-archive") == "internet_archive"
    assert get_portal("BNC ROMA").key == "bnc_roma"
    assert get_portal("non_esiste") is None


def test_roadmap_priority_values_are_known():
    priorities = {portal.roadmap_priority for portal in PORTAL_REGISTRY.values()}
    assert priorities == {"consolidate", "maintain_with_warning", "do_not_extend"}


def test_each_priority_has_a_warning_message_key():
    priorities = {portal.roadmap_priority for portal in PORTAL_REGISTRY.values()}
    assert set(PORTAL_WARNING_MESSAGE_KEYS) == priorities
    assert get_portal_warning_message_key("gallica") == PORTAL_WARNING_MESSAGE_KEYS["consolidate"]
    assert get_portal_warning_message_key("antenati") == PORTAL_WARNING_MESSAGE_KEYS["maintain_with_warning"]
    assert get_portal_warning_message_key("matricula") == PORTAL_WARNING_MESSAGE_KEYS["do_not_extend"]
    assert get_portal_warning_message_key("non_esiste") is None


def test_portal_referer_capability_matches_existing_special_cases():
    assert get_portal_referer("gallica") == "https://gallica.bnf.fr"
    assert get_portal_referer("BNC ROMA") == "http://digitale.bnc.roma.sbn.it"
    assert get_portal_referer("manifest_diretto") is None
    assert get_portal_referer("antenati") is None
    assert get_portal_referer("bncf_teca", "https://teca.bncf.firenze.sbn.it/viewer") == "https://teca.bncf.firenze.sbn.it"
