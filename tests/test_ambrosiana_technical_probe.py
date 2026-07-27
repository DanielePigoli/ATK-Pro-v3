from __future__ import annotations

from pathlib import Path

import verify_ambrosiana_technical_probe as probe


def test_extract_candidates_finds_comperio_record_and_diamm_manifest():
    html = """
    <a href="https://ambrosiana.comperio.it/opac/detail/view/ambro:catalog:24203">A 24 inf.</a>
    <a href="https://iiif.diamm.net/manifests/I-Ma-A-24_Inf/manifest.json">manifest</a>
    """

    candidates = probe.extract_candidates(html, "https://ambrosiana.comperio.it/")
    by_role = {candidate.role: candidate for candidate in candidates}

    assert by_role["comperio_record"].kind == "catalog_record"
    assert by_role["comperio_record"].identifier == "24203"
    assert by_role["external_diamm_manifest"].kind == "manifest"
    assert by_role["external_diamm_manifest"].identifier == "I-Ma-A-24_Inf"


def test_extract_candidates_finds_viewer_info_json_and_cantaloupe_images():
    html = """
    <a href="/mirador/?manifest=https://example.org/iiif/manifest.json">Mirador</a>
    <a href="https://example.org/iiif/page/info.json">info</a>
    <img src="https://ambrosiana.example/cantaloupe/iiif/2/abc/full/500,/0/default.jpg">
    """

    candidates = probe.extract_candidates(html, "https://ambrosiana.comperio.it/opac/detail/view/ambro:catalog:24203")
    roles = {candidate.role for candidate in candidates}
    kinds = {candidate.kind for candidate in candidates}

    assert "mirador_viewer" in roles
    assert "cantaloupe_image" in roles
    assert "iiif_info" in kinds
    assert "manifest" in kinds


def test_extract_candidates_finds_unicatt_viewer_manifest_and_no_downloadable_notice():
    html = """
    <a href="https://digitallibrary.unicatt.it/veneranda/0b02da82800d10a0">viewer</a>
    <a href="https://digitallibrary.unicatt.it/veneranda/data/public/manifests/0b/02/da/82/80/0d/10/a0/0b02da82800d10a0.json">manifest</a>
    <div>Restriction of use: No Downloadable</div>
    """

    candidates = probe.extract_candidates(html, "https://digitallibrary.unicatt.it/veneranda/0b02da82800d10a0")
    by_role = {candidate.role: candidate for candidate in candidates}

    assert by_role["unicatt_viewer_page"].kind == "viewer"
    assert by_role["unicatt_public_manifest"].kind == "manifest"
    assert by_role["no_downloadable_notice"].kind == "rights_notice"
    assert by_role["no_downloadable_notice"].source == "No Downloadable"


def test_extract_candidates_ignores_duplicates_and_marks_site_assets():
    html = """
    <a href="#content">anchor</a>
    <a href="mailto:info@example.test">mail</a>
    <img src="/sites/ambrosiana/assets/logo.png">
    <a href="https://ambrosiana.comperio.it/opac/detail/view/ambro:catalog:24203">record</a>
    <a href="https://ambrosiana.comperio.it/opac/detail/view/ambro:catalog:24203">same record</a>
    """

    candidates = probe.extract_candidates(html, "https://ambrosiana.comperio.it/")
    by_role = {candidate.role: candidate for candidate in candidates}

    assert len(candidates) == 2
    assert by_role["site_asset"].kind == "image"
    assert by_role["comperio_record"].identifier == "24203"


def test_write_report_creates_csv(tmp_path: Path):
    report = tmp_path / "ambrosiana_probe.csv"
    probe.write_report(
        report,
        [
            probe.ProbeCandidate(
                kind="catalog_record",
                role="comperio_record",
                identifier="24203",
                url="https://ambrosiana.comperio.it/opac/detail/view/ambro:catalog:24203",
                source="html_attribute",
            )
        ],
    )

    text = report.read_text(encoding="utf-8")
    assert "kind,role,identifier,url,source" in text
    assert "24203" in text


def test_evaluate_readiness_holds_when_official_manifest_is_no_downloadable():
    readiness = probe._evaluate_readiness(
        [
            probe.ProbeCandidate(
                kind="viewer",
                role="unicatt_viewer_page",
                identifier="0b02da82800d10a0",
                url="https://digitallibrary.unicatt.it/veneranda/0b02da82800d10a0",
                source="html_attribute",
            ),
            probe.ProbeCandidate(
                kind="manifest",
                role="unicatt_public_manifest",
                identifier="0b02da82800d10a0",
                url="https://digitallibrary.unicatt.it/veneranda/data/public/manifests/0b/02/da/82/80/0d/10/a0/0b02da82800d10a0.json",
                source="html_attribute",
            ),
            probe.ProbeCandidate(
                kind="rights_notice",
                role="no_downloadable_notice",
                identifier="",
                url="https://digitallibrary.unicatt.it/veneranda/0b02da82800d10a0",
                source="No Downloadable",
            ),
        ]
    )

    assert readiness.startswith("GO/NO-GO: HOLD")


def test_evaluate_readiness_holds_when_only_external_manifest_emerges():
    readiness = probe._evaluate_readiness(
        [
            probe.ProbeCandidate(
                kind="manifest",
                role="external_diamm_manifest",
                identifier="I-Ma-A-24_Inf",
                url="https://iiif.diamm.net/manifests/I-Ma-A-24_Inf/manifest.json",
                source="html_attribute",
            )
        ]
    )

    assert readiness.startswith("GO/NO-GO: HOLD")
