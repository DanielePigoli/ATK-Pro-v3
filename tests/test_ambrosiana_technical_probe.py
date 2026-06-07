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
