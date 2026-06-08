from __future__ import annotations

from pathlib import Path

import verify_orientales_technical_probe as probe


def test_extract_candidates_finds_unior_page_and_omeka_records():
    html = """
    <a href="https://www.unior.it/it/biblioteche/servizi-gli-utenti/biblioteca-digitale">Biblioteca digitale</a>
    <a href="https://orientales.unior.it/s/orientales/item/321">item</a>
    <a href="https://orientales.unior.it/s/orientales/media/654">media</a>
    <a href="https://orientales.unior.it/api/items/321">api item</a>
    <a href="https://orientales.unior.it/api/media/654">api media</a>
    """

    candidates = probe.extract_candidates(html, "https://www.unior.it/")
    by_role = {candidate.role: candidate for candidate in candidates}

    assert by_role["orientales_page"].kind == "portal_page"
    assert by_role["omeka_item"].kind == "catalog_record"
    assert by_role["omeka_item"].identifier == "321"
    assert by_role["omeka_media"].kind == "media_record"
    assert by_role["omeka_api_items"].kind == "api_record"
    assert by_role["omeka_api_media"].kind == "api_record"


def test_extract_candidates_finds_mirador_manifest_info_image_and_text_derivatives():
    html = """
    <a href="/mirador?manifest=https%3A%2F%2Forientales.unior.it%2Fiiif%2Fabc%2Fmanifest.json">Mirador</a>
    <a href="https://orientales.unior.it/iiif/abc/manifest.json">manifest</a>
    <a href="https://orientales.unior.it/iiif/abc/page-1/info.json">info</a>
    <img src="https://orientales.unior.it/iiif/abc/page-1/full/1000,/0/default.jpg">
    <a href="https://orientales.unior.it/files/ocr/page-1.xml">ocr</a>
    <a href="https://orientales.unior.it/files/alto/page-1.alto.xml">alto</a>
    <a href="https://orientales.unior.it/api/items/321?format=jsonld">metadata</a>
    """

    candidates = probe.extract_candidates(html, "https://orientales.unior.it/s/orientales/item/321")
    kinds = {candidate.kind for candidate in candidates}
    roles = {candidate.role for candidate in candidates}

    assert {"viewer", "manifest", "iiif_info", "image", "text_derivative", "api_record"} <= kinds
    assert "mirador_viewer" in roles
    assert "viewer_manifest_parameter" in roles
    assert "iiif_content_image" in roles
    assert "alto_ocr" in roles
    assert "ocr_or_transcription" in roles


def test_extract_candidates_ignores_duplicates_and_marks_site_assets():
    html = """
    <a href="#main">anchor</a>
    <a href="mailto:info@example.test">mail</a>
    <img src="/themes/default/asset/img/logo.png">
    <a href="https://orientales.unior.it/s/orientales/item/321">item</a>
    <a href="https://orientales.unior.it/s/orientales/item/321">same item</a>
    """

    candidates = probe.extract_candidates(html, "https://orientales.unior.it/")
    by_role = {candidate.role: candidate for candidate in candidates}

    assert len(candidates) == 2
    assert by_role["site_asset"].kind == "image"
    assert by_role["omeka_item"].identifier == "321"


def test_write_report_creates_csv(tmp_path: Path):
    report = tmp_path / "orientales_probe.csv"
    probe.write_report(
        report,
        [
            probe.ProbeCandidate(
                kind="manifest",
                role="candidate",
                identifier="abc",
                url="https://orientales.unior.it/iiif/abc/manifest.json",
                source="html_attribute",
            )
        ],
    )

    text = report.read_text(encoding="utf-8")
    assert "kind,role,identifier,url,source" in text
    assert "orientales" in text
