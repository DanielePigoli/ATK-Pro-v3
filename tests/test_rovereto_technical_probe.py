from __future__ import annotations

from pathlib import Path

import verify_rovereto_technical_probe as probe


ITEM_UUID = "e4199e9b-c79b-4c3d-b157-be2dcfc0407f"
BUNDLE_UUID = "6c76babc-df6f-41a7-9084-40279e01b800"
BITSTREAM_UUID = "13077fcb-4069-4034-8cfe-d815f0808e04"


def test_extract_candidates_finds_entity_handle_and_rest_links():
    html = f"""
    <a href="https://digitallibrary.bibliotecacivica.rovereto.tn.it/entities/publication/{ITEM_UUID}">entity</a>
    <a href="https://digitallibrary.bibliotecacivica.rovereto.tn.it/handle/20.500.14379/35083">handle</a>
    <a href="https://digitallibrary.bibliotecacivica.rovereto.tn.it/server/api/core/items/{ITEM_UUID}">api</a>
    <a href="https://digitallibrary.bibliotecacivica.rovereto.tn.it/server/api/core/bitstreams/{BITSTREAM_UUID}/content">content</a>
    """

    candidates = probe.extract_candidates(html, "https://digitallibrary.bibliotecacivica.rovereto.tn.it/")
    by_role = {candidate.role: candidate for candidate in candidates}

    assert by_role["dspace_publication"].kind == "entity"
    assert by_role["dspace_publication"].identifier == ITEM_UUID
    assert by_role["persistent_handle"].identifier == "20.500.14379/35083"
    assert by_role["dspace_rest_item"].kind == "api_item"
    assert by_role["bitstream_content"].kind == "bitstream"


def test_extract_candidates_finds_manifest_info_viewer_and_files():
    html = """
    <a href="/iiif/item/123/manifest">manifest</a>
    <a href="/iiif/2/abc/info.json">info</a>
    <a href="/mirador?manifest=https://example.test/manifest.json">Mirador</a>
    <a href="/downloads/book.pdf">PDF</a>
    <img src="/assets/logo.png">
    <img src="/files/photo.jpg">
    """

    candidates = probe.extract_candidates(html, "https://digitallibrary.bibliotecacivica.rovereto.tn.it/entities/picture/2cbeaeab-833a-48c2-9b39-29484ed1c681")
    roles = {candidate.role for candidate in candidates}
    kinds = {candidate.kind for candidate in candidates}

    assert "mirador_viewer" in roles
    assert "site_asset" in roles
    assert "candidate" in roles
    assert {"manifest", "iiif_info", "pdf", "image", "viewer"} <= kinds


def test_extract_candidates_ignores_duplicates_and_non_download_links():
    html = f"""
    <a href="#content">anchor</a>
    <a href="mailto:info@example.test">mail</a>
    <a href="/entities/publication/{ITEM_UUID}">entity</a>
    <a href="/entities/publication/{ITEM_UUID}">same entity</a>
    """

    candidates = probe.extract_candidates(html, "https://digitallibrary.bibliotecacivica.rovereto.tn.it/")

    assert candidates == [
        probe.ProbeCandidate(
            kind="api_item",
            role="dspace_rest_item",
            identifier=ITEM_UUID,
            url=f"https://digitallibrary.bibliotecacivica.rovereto.tn.it/server/api/core/items/{ITEM_UUID}",
            source="derived_from_entity",
        ),
        probe.ProbeCandidate(
            kind="entity",
            role="dspace_publication",
            identifier=ITEM_UUID,
            url=f"https://digitallibrary.bibliotecacivica.rovereto.tn.it/entities/publication/{ITEM_UUID}",
            source="html_attribute",
        ),
    ]


def test_extract_candidates_classifies_input_entity_and_derives_api_item():
    entity_url = f"https://digitallibrary.bibliotecacivica.rovereto.tn.it/entities/picture/{ITEM_UUID}"

    candidates = probe.extract_candidates("<html></html>", entity_url)
    by_source = {candidate.source: candidate for candidate in candidates}
    by_role = {candidate.role: candidate for candidate in candidates}

    assert by_source["input_url"].kind == "entity"
    assert by_source["input_url"].role == "dspace_picture"
    assert by_role["dspace_rest_item"].url == (
        f"https://digitallibrary.bibliotecacivica.rovereto.tn.it/server/api/core/items/{ITEM_UUID}"
    )
    assert by_role["dspace_rest_item"].source == "derived_from_entity"


def test_extract_candidates_reads_json_hal_links_and_subresources():
    html = f"""
    {{
        "_links": {{
            "self": {{"href": "https://digitallibrary.bibliotecacivica.rovereto.tn.it/server/api/core/items/{ITEM_UUID}"}},
            "bundles": {{"href": "https://digitallibrary.bibliotecacivica.rovereto.tn.it/server/api/core/items/{ITEM_UUID}/bundles"}},
            "thumbnail": {{"href": "https://digitallibrary.bibliotecacivica.rovereto.tn.it/server/api/core/items/{ITEM_UUID}/thumbnail"}},
            "bundle": {{"href": "https://digitallibrary.bibliotecacivica.rovereto.tn.it/server/api/core/bundles/{BUNDLE_UUID}"}},
            "bitstreams": {{"href": "https://digitallibrary.bibliotecacivica.rovereto.tn.it/server/api/core/bundles/{BUNDLE_UUID}/bitstreams"}},
            "content": {{"href": "https://digitallibrary.bibliotecacivica.rovereto.tn.it/server/api/core/bitstreams/{BITSTREAM_UUID}/content"}}
        }}
    }}
    """

    candidates = probe.extract_candidates(
        html,
        f"https://digitallibrary.bibliotecacivica.rovereto.tn.it/server/api/core/items/{ITEM_UUID}/bundles",
    )
    by_role = {candidate.role: candidate for candidate in candidates}

    assert by_role["dspace_rest_item"].source == "json_link"
    assert by_role["dspace_item_bundles"].kind == "api_item"
    assert by_role["dspace_item_thumbnail"].identifier == ITEM_UUID
    assert by_role["bundle_metadata"].kind == "bundle"
    assert by_role["bundle_bitstreams"].identifier == BUNDLE_UUID
    assert by_role["bitstream_content"].kind == "bitstream"


def test_write_report_creates_csv(tmp_path: Path):
    report = tmp_path / "rovereto_probe.csv"
    probe.write_report(
        report,
        [
            probe.ProbeCandidate(
                kind="entity",
                role="dspace_picture",
                identifier="2cbeaeab-833a-48c2-9b39-29484ed1c681",
                url="https://digitallibrary.bibliotecacivica.rovereto.tn.it/entities/picture/2cbeaeab-833a-48c2-9b39-29484ed1c681",
                source="html_attribute",
            )
        ],
    )

    text = report.read_text(encoding="utf-8")
    assert "kind,role,identifier,url,source" in text
    assert "2cbeaeab" in text
