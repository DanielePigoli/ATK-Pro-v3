from __future__ import annotations

from pathlib import Path

import verify_bub_technical_probe as probe


def test_extract_candidates_finds_bub_page_record_and_mirador_manifest():
    html = """
    <a href="https://bub.unibo.it/it/bub-digitale">BUB Digitale</a>
    <a href="/it/collezioni/bollettini-parrocchiali">Bollettini parrocchiali</a>
    <a href="/mirador?manifest=https%3A%2F%2Fiiif.bub.unibo.it%2Fiiif%2Fabc123%2Fmanifest.json">Mirador</a>
    """

    candidates = probe.extract_candidates(html, "https://bub.unibo.it/it/bub-digitale")
    by_role = {candidate.role: candidate for candidate in candidates}

    assert by_role["bub_digitale_page"].kind == "portal_page"
    assert by_role["bub_record_or_collection"].kind == "catalog_record"
    assert by_role["mirador_viewer"].kind == "viewer"
    assert by_role["viewer_manifest_parameter"].kind == "manifest"
    assert by_role["viewer_manifest_parameter"].url == "https://iiif.bub.unibo.it/iiif/abc123/manifest.json"


def test_extract_candidates_finds_manifest_info_and_iiif_image():
    html = """
    <a href="https://iiif.bub.unibo.it/iiif/ms-001/manifest.json">manifest</a>
    <a href="https://iiif.bub.unibo.it/iiif/ms-001/page-0001/info.json">info</a>
    <img src="https://iiif.bub.unibo.it/iiif/ms-001/page-0001/full/1000,/0/default.jpg">
    """

    candidates = probe.extract_candidates(html, "https://bub.unibo.it/")
    kinds = {candidate.kind for candidate in candidates}
    roles = {candidate.role for candidate in candidates}

    assert {"manifest", "iiif_info", "image"} <= kinds
    assert "iiif_content_image" in roles


def test_extract_candidates_ignores_duplicates_and_marks_site_assets():
    html = """
    <a href="#main">anchor</a>
    <a href="mailto:info@example.test">mail</a>
    <img src="/++theme++bub/logo.png">
    <a href="/it/collezioni/bollettini-parrocchiali">record</a>
    <a href="/it/collezioni/bollettini-parrocchiali">same record</a>
    """

    candidates = probe.extract_candidates(html, "https://bub.unibo.it/it/bub-digitale")
    by_role = {candidate.role: candidate for candidate in candidates}

    assert len(candidates) == 2
    assert by_role["site_asset"].kind == "image"
    assert by_role["bub_record_or_collection"].identifier == "bollettini-parrocchiali"


def test_extract_candidates_marks_plone_page_images_separately():
    html = """
    <img src="/it/immagini/canale-bub-digitale-1/bollettini-parrocchiali/@@images/cb9014fc-19f2-4eb9-a8a1-00b449fba39b.png">
    <img src="https://bub.unibo.it/logo.png">
    """

    candidates = probe.extract_candidates(html, "https://bub.unibo.it/it/bub-digitale")
    by_role = {candidate.role: candidate for candidate in candidates}

    assert by_role["plone_page_image"].kind == "image"
    assert by_role["plone_page_image"].identifier == "cb9014fc-19f2-4eb9-a8a1-00b449fba39b.png"
    assert by_role["site_asset"].kind == "image"


def test_extract_candidates_ignores_non_url_attribute_values():
    html = """
    <meta content="IE=edge">
    <span data-label="Mensile" data-value="True" data-state="is-opened">x</span>
    <a href="/it/bub-digitale/bollettini-parrocchiali">real page</a>
    """

    candidates = probe.extract_candidates(html, "https://bub.unibo.it/it/bub-digitale/bollettini-parrocchiali")

    assert candidates == [
        probe.ProbeCandidate(
            kind="portal_page",
            role="bub_digitale_page",
            identifier="",
            url="https://bub.unibo.it/it/bub-digitale/bollettini-parrocchiali",
            source="html_attribute",
        )
    ]


def test_write_report_creates_csv(tmp_path: Path):
    report = tmp_path / "bub_probe.csv"
    probe.write_report(
        report,
        [
            probe.ProbeCandidate(
                kind="manifest",
                role="candidate",
                identifier="abc123",
                url="https://iiif.bub.unibo.it/iiif/abc123/manifest.json",
                source="html_attribute",
            )
        ],
    )

    text = report.read_text(encoding="utf-8")
    assert "kind,role,identifier,url,source" in text
    assert "abc123" in text
