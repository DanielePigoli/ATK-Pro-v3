import src.manifest_utils as manifest_utils
from datetime import date
import json

from src.portal_registry import (
    PORTAL_REGISTRY,
    PORTAL_WARNING_MESSAGE_KEYS,
    RECORD_MODE_POLICIES,
    R_POLICY_LABELS,
    TECHNICAL_FAMILIES,
    get_effective_portal_policy,
    get_portal,
    get_portal_groups,
    get_portal_referer,
    get_portal_record_mode_policy,
    get_portal_technical_family,
    get_portal_tile_download_policy,
    get_portal_warning_message_key,
    normalize_portal_key,
    portal_keys,
    portals_by_technical_family,
    write_portal_policy_override_template,
)


def test_registry_has_expected_portal_count_and_unique_keys():
    keys = portal_keys()
    assert len(keys) == 21
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
    assert get_portal_referer("biblioteca_digitale_siena") == "https://bds.comune.siena.it"
    assert get_portal_referer("biblioteca_digitale_trentina") == "https://bdt.bibcom.trento.it"
    assert get_portal_referer("manifest_diretto") is None
    assert get_portal_referer("antenati") is None
    assert get_portal_referer("bncf_teca", "https://teca.bncf.firenze.sbn.it/viewer") == "https://teca.bncf.firenze.sbn.it"


def test_technical_family_values_are_known():
    families = {portal.technical_family for portal in PORTAL_REGISTRY.values()}
    assert families == TECHNICAL_FAMILIES


def test_technical_family_lookup_and_grouping():
    assert get_portal_technical_family("gallica") == "iiif_direct"
    assert get_portal_technical_family("antenati") == "iiif_discovery"
    assert get_portal_technical_family("bncf_teca") == "hybrid_manifest"
    assert get_portal_technical_family("non_esiste") is None

    iiif_direct = {portal.key for portal in portals_by_technical_family("iiif_direct")}
    synthetic = {portal.key for portal in portals_by_technical_family("synthetic_manifest")}

    assert "europeana" in iiif_direct
    assert "memooria" in iiif_direct
    assert "matricula" in synthetic
    assert "internet_archive" in synthetic


def test_tile_download_policy_marks_heidelberg_rate_limit():
    assert get_portal_tile_download_policy("heidelberg") == (1, 0.3)
    assert get_portal_tile_download_policy("biblioteca_digitale_siena") == (1, 0.3)
    assert get_portal_tile_download_policy("gallica") == (None, 0.0)
    assert get_portal_tile_download_policy("non_esiste") == (None, 0.0)


def test_record_mode_policy_values_are_known_and_classified():
    policies = {portal.record_mode_policy for portal in PORTAL_REGISTRY.values()}
    assert policies <= RECORD_MODE_POLICIES
    assert set(R_POLICY_LABELS) == RECORD_MODE_POLICIES

    assert get_portal_record_mode_policy("antenati") == "r_ok"
    assert get_portal_record_mode_policy("gallica") == "r_ok"
    assert get_portal_record_mode_policy("bncf_teca") == "d_only"
    assert get_portal_record_mode_policy("museogalileo") == "d_only"
    assert get_portal_record_mode_policy("matricula") == "r_limited"
    assert get_portal_record_mode_policy("biblioteca_digitale_siena") == "r_limited"
    assert get_portal_record_mode_policy("biblioteca_digitale_trentina") == "r_limited"
    assert get_portal_record_mode_policy("manifest_diretto") == "variable"


def test_effective_policy_marks_stale_checks_prudently():
    fresh = get_effective_portal_policy("gallica", today=date(2026, 6, 2))
    stale = get_effective_portal_policy("gallica", today=date(2026, 12, 2))

    assert fresh is not None
    assert fresh.record_mode_policy == "r_ok"
    assert not fresh.recheck_due
    assert stale is not None
    assert stale.record_mode_policy == "r_ok"
    assert stale.recheck_due


def test_manifest_direct_policy_is_variable_not_periodically_stale():
    policy = get_effective_portal_policy("manifest_diretto", today=date(2026, 12, 2))

    assert policy is not None
    assert policy.record_mode_policy == "variable"
    assert not policy.recheck_due


def test_local_policy_override_can_update_record_mode_without_release(tmp_path):
    override_path = tmp_path / "portal_policy_overrides.json"
    override_path.write_text(
        json.dumps(
            {
                "version": 1,
                "portals": {
                    "bncf_teca": {
                        "record_mode_policy": "r_limited",
                        "policy_checked_at": "2026-06-01",
                        "policy_recheck_days": 365,
                        "policy_source_urls": ["https://example.test/terms"],
                    }
                },
            }
        ),
        encoding="utf-8",
    )

    policy = get_effective_portal_policy("bncf_teca", local_policy_path=override_path, today=date(2026, 6, 2))

    assert policy is not None
    assert policy.policy_source == "local"
    assert policy.record_mode_policy == "r_limited"
    assert policy.policy_checked_at == "2026-06-01"
    assert policy.policy_source_urls == ("https://example.test/terms",)
    assert not policy.recheck_due


def test_write_portal_policy_override_template(tmp_path):
    output_path = write_portal_policy_override_template(tmp_path / "portal_policy_overrides.json")
    data = json.loads(output_path.read_text(encoding="utf-8"))

    assert set(data["portals"]) == set(PORTAL_REGISTRY)
    assert data["portals"]["antenati"]["record_mode_policy"] == "r_ok"
    assert data["portals"]["manifest_diretto"]["record_mode_policy"] == "variable"
