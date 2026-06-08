from __future__ import annotations

from pathlib import Path

import verify_ficlit_technical_probe as probe


def test_extract_candidates_finds_ficlit_page_item_media_and_api():
    html = """
    <a href="https://dl.ficlit.unibo.it/s/lib/page/progetto">Progetto</a>
    <a href="/s/lib/item/123">item</a>
    <a href="/s/lib/media/456">media</a>
    <a href="/api/items/123">api item</a>
    <a href="/api/media/456">api media</a>
    """

    candidates = probe.extract_candidates(html, "https://dl.ficlit.unibo.it/s/lib/page/progetto")
    by_role = {candidate.role: candidate for candidate in candidates}

    assert by_role["ficlit_page"].kind == "portal_page"
    assert by_role["omeka_item"].kind == "catalog_record"
    assert by_role["omeka_item"].identifier == "123"
    assert by_role["omeka_media"].kind == "media_record"
    assert by_role["omeka_media"].identifier == "456"
    assert by_role["omeka_api_items"].kind == "api_record"
    assert by_role["omeka_api_media"].kind == "api_record"


def test_extract_candidates_finds_mirador_manifest_info_and_iiif_image():
    html = """
    <a href="/mirador?manifest=https%3A%2F%2Fdl.ficlit.unibo.it%2Fiiif%2Fabc%2Fmanifest.json">Mirador</a>
    <a href="https://dl.ficlit.unibo.it/iiif/abc/manifest.json">manifest</a>
    <a href="https://dl.ficlit.unibo.it/iiif/abc/page-1/info.json">info</a>
    <img src="https://dl.ficlit.unibo.it/iiif/abc/page-1/full/1000,/0/default.jpg">
    """

    candidates = probe.extract_candidates(html, "https://dl.ficlit.unibo.it/s/lib/item/123")
    kinds = {candidate.kind for candidate in candidates}
    roles = {candidate.role for candidate in candidates}

    assert {"viewer", "manifest", "iiif_info", "image"} <= kinds
    assert "mirador_viewer" in roles
    assert "viewer_manifest_parameter" in roles
    assert "iiif_content_image" in roles


def test_extract_candidates_ignores_duplicates_and_marks_site_assets():
    html = """
    <a href="#main">anchor</a>
    <a href="mailto:info@example.test">mail</a>
    <img src="/themes/default/asset/img/logo.png">
    <a href="/s/lib/item/123">item</a>
    <a href="/s/lib/item/123">same item</a>
    """

    candidates = probe.extract_candidates(html, "https://dl.ficlit.unibo.it/s/lib/page/progetto")
    by_role = {candidate.role: candidate for candidate in candidates}

    assert len(candidates) == 2
    assert by_role["site_asset"].kind == "image"
    assert by_role["omeka_item"].identifier == "123"


def test_write_report_creates_csv(tmp_path: Path):
    report = tmp_path / "ficlit_probe.csv"
    probe.write_report(
        report,
        [
            probe.ProbeCandidate(
                kind="api_record",
                role="omeka_api_items",
                identifier="123",
                url="https://dl.ficlit.unibo.it/api/items/123",
                source="html_attribute",
            )
        ],
    )

    text = report.read_text(encoding="utf-8")
    assert "kind,role,identifier,url,source" in text
    assert "omeka_api_items" in text
