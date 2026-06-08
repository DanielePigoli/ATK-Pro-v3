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
            "content": {{"href": "https://digitallibrary.bibliotecacivica.rovereto.tn.it/server/api/core/bitstreams/{BITSTREAM_UUID}/content"}},
            "format": {{"href": "https://digitallibrary.bibliotecacivica.rovereto.tn.it/server/api/core/bitstreams/{BITSTREAM_UUID}/format"}},
            "thumbnail": {{"href": "https://digitallibrary.bibliotecacivica.rovereto.tn.it/server/api/core/bitstreams/{BITSTREAM_UUID}/thumbnail"}}
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
    assert by_role["bitstream_format"].identifier == BITSTREAM_UUID
    assert by_role["bitstream_thumbnail"].identifier == BITSTREAM_UUID


def test_collect_candidates_follows_json_links_with_limited_depth(monkeypatch):
    item_url = f"https://digitallibrary.bibliotecacivica.rovereto.tn.it/server/api/core/items/{ITEM_UUID}"
    bundles_url = f"{item_url}/bundles"
    bundle_url = f"https://digitallibrary.bibliotecacivica.rovereto.tn.it/server/api/core/bundles/{BUNDLE_UUID}"
    bitstreams_url = f"{bundle_url}/bitstreams"
    bitstream_url = f"https://digitallibrary.bibliotecacivica.rovereto.tn.it/server/api/core/bitstreams/{BITSTREAM_UUID}"
    content_url = f"{bitstream_url}/content"
    format_url = f"{bitstream_url}/format"
    responses = {
        item_url: f'{{"_links": {{"bundles": {{"href": "{bundles_url}"}}}}}}',
        bundles_url: f'{{"_embedded": {{"bundles": [{{"_links": {{"self": {{"href": "{bundle_url}"}}}}}}]}}}}',
        bundle_url: f'{{"_links": {{"bitstreams": {{"href": "{bitstreams_url}"}}}}}}',
        bitstreams_url: f'{{"_embedded": {{"bitstreams": [{{"_links": {{"self": {{"href": "{bitstream_url}"}}, "content": {{"href": "{content_url}"}}}}}}]}}}}',
        bitstream_url: f'{{"_links": {{"content": {{"href": "{content_url}"}}, "format": {{"href": "{format_url}"}}}}}}',
        format_url: '{"format": "JPEG"}',
    }

    def fake_load_url(url: str, timeout: int) -> str:
        return responses[url]

    monkeypatch.setattr(probe, "_load_url", fake_load_url)

    candidates = probe.collect_candidates(
        f'{{"_links": {{"self": {{"href": "{item_url}"}}}}}}',
        item_url,
        follow_json=True,
        max_depth=5,
    )
    by_role = {candidate.role: candidate for candidate in candidates}

    assert by_role["dspace_item_bundles"].url == bundles_url
    assert by_role["bundle_metadata"].url == bundle_url
    assert by_role["bundle_bitstreams"].url == bitstreams_url
    assert by_role["bitstream_metadata"].url == bitstream_url
    assert by_role["bitstream_content"].url == content_url
    assert by_role["bitstream_format"].url == format_url


def test_collect_candidates_does_not_follow_content_links(monkeypatch):
    content_url = f"https://digitallibrary.bibliotecacivica.rovereto.tn.it/server/api/core/bitstreams/{BITSTREAM_UUID}/content"
    calls: list[str] = []

    def fake_load_url(url: str, timeout: int) -> str:
        calls.append(url)
        return ""

    monkeypatch.setattr(probe, "_load_url", fake_load_url)

    candidates = probe.collect_candidates(
        f'{{"_links": {{"content": {{"href": "{content_url}"}}}}}}',
        content_url,
        follow_json=True,
        max_depth=2,
    )

    assert calls == []
    assert candidates == [
        probe.ProbeCandidate(
            kind="bitstream",
            role="bitstream_content",
            identifier=BITSTREAM_UUID,
            url=content_url,
            source="input_url",
        )
    ]


def test_summarize_bitstreams_reads_metadata_and_format_without_content(monkeypatch):
    bitstream_url = f"https://digitallibrary.bibliotecacivica.rovereto.tn.it/server/api/core/bitstreams/{BITSTREAM_UUID}"
    content_url = f"{bitstream_url}/content"
    format_url = f"{bitstream_url}/format"
    bundle_url = f"https://digitallibrary.bibliotecacivica.rovereto.tn.it/server/api/core/bundles/{BUNDLE_UUID}"
    thumbnail_url = f"{bitstream_url}/thumbnail"
    opened: list[str] = []
    responses = {
        bitstream_url: f"""{{
            "uuid": "{BITSTREAM_UUID}",
            "name": "page-10.jpg",
            "sequenceId": 10,
            "sizeBytes": 123456,
            "checkSum": {{"algorithm": "MD5", "value": "abc123"}},
            "_links": {{
                "content": {{"href": "{content_url}"}},
                "format": {{"href": "{format_url}"}},
                "bundle": {{"href": "{bundle_url}"}},
                "thumbnail": {{"href": "{thumbnail_url}"}}
            }}
        }}""",
        format_url: '{"shortDescription": "JPEG", "mimetype": "image/jpeg"}',
    }

    def fake_load_url(url: str, timeout: int) -> str:
        opened.append(url)
        return responses[url]

    monkeypatch.setattr(probe, "_load_url", fake_load_url)

    summaries = probe.summarize_bitstreams(
        [
            probe.ProbeCandidate(
                kind="bitstream",
                role="bitstream_metadata",
                identifier=BITSTREAM_UUID,
                url=bitstream_url,
                source="json_link",
            ),
            probe.ProbeCandidate(
                kind="bitstream",
                role="bitstream_content",
                identifier=BITSTREAM_UUID,
                url=content_url,
                source="json_link",
            ),
        ]
    )

    assert opened == [bitstream_url, format_url]
    assert summaries == [
        probe.BitstreamSummary(
            identifier=BITSTREAM_UUID,
            name="page-10.jpg",
            category="thumbnail_or_cover",
            download_candidate="no",
            page_number="",
            sequence_id="10",
            size_bytes="123456",
            checksum="abc123",
            checksum_algorithm="MD5",
            format_label="JPEG",
            format_mimetype="image/jpeg",
            metadata_url=bitstream_url,
            content_url=content_url,
            bundle_url=bundle_url,
            thumbnail_url=thumbnail_url,
        )
    ]


def test_write_bitstream_report_creates_csv(tmp_path: Path):
    report = tmp_path / "bitstreams.csv"
    probe.write_bitstream_report(
        report,
        [
            probe.BitstreamSummary(
                identifier=BITSTREAM_UUID,
                name="page-1.jpg",
                category="thumbnail_or_cover",
                download_candidate="no",
                page_number="",
                sequence_id="1",
                size_bytes="42",
                checksum="abc123",
                checksum_algorithm="MD5",
                format_label="JPEG",
                format_mimetype="image/jpeg",
                metadata_url=f"https://digitallibrary.bibliotecacivica.rovereto.tn.it/server/api/core/bitstreams/{BITSTREAM_UUID}",
                content_url=f"https://digitallibrary.bibliotecacivica.rovereto.tn.it/server/api/core/bitstreams/{BITSTREAM_UUID}/content",
                bundle_url=f"https://digitallibrary.bibliotecacivica.rovereto.tn.it/server/api/core/bundles/{BUNDLE_UUID}",
                thumbnail_url="",
            )
        ],
    )

    text = report.read_text(encoding="utf-8")
    assert "identifier,name,category,download_candidate,page_number,sequence_id,size_bytes" in text
    assert "page-1.jpg" in text
    assert "image/jpeg" in text


def test_classify_bitstream_marks_pages_and_derivatives():
    assert probe._classify_bitstream("iiifpdf-0.png", "image/png") == ("page_image", "yes", "1")
    assert probe._classify_bitstream("iiifpdf-128.png", "image/png") == ("page_image", "yes", "129")
    assert probe._classify_bitstream("book.pdf", "application/pdf") == ("source_pdf", "yes", "")
    assert probe._classify_bitstream("license.txt", "text/plain") == ("license", "no", "")
    assert probe._classify_bitstream("book.pdf.txt", "text/plain") == ("text_derivative", "no", "")
    assert probe._classify_bitstream("book.pdf.jpg", "image/jpeg") == ("thumbnail_or_cover", "no", "")


def test_summarize_bitstream_rows_reports_categories_and_page_gaps():
    summaries = [
        probe.BitstreamSummary(
            identifier="page-1",
            name="iiifpdf-0.png",
            category="page_image",
            download_candidate="yes",
            page_number="1",
            sequence_id="5",
            size_bytes="100",
            checksum="",
            checksum_algorithm="",
            format_label="PNG",
            format_mimetype="image/png",
            metadata_url="https://example.test/1",
            content_url="https://example.test/1/content",
            bundle_url="",
            thumbnail_url="",
        ),
        probe.BitstreamSummary(
            identifier="page-3",
            name="iiifpdf-2.png",
            category="page_image",
            download_candidate="yes",
            page_number="3",
            sequence_id="7",
            size_bytes="100",
            checksum="",
            checksum_algorithm="",
            format_label="PNG",
            format_mimetype="image/png",
            metadata_url="https://example.test/3",
            content_url="https://example.test/3/content",
            bundle_url="",
            thumbnail_url="",
        ),
        probe.BitstreamSummary(
            identifier="pdf",
            name="book.pdf",
            category="source_pdf",
            download_candidate="yes",
            page_number="",
            sequence_id="2",
            size_bytes="200",
            checksum="",
            checksum_algorithm="",
            format_label="PDF",
            format_mimetype="application/pdf",
            metadata_url="https://example.test/pdf",
            content_url="https://example.test/pdf/content",
            bundle_url="",
            thumbnail_url="",
        ),
    ]

    lines = probe._summarize_bitstream_rows(summaries)

    assert "Bitstream sintetizzati: 3" in lines
    assert "- page_image (yes): 2" in lines
    assert "- source_pdf (yes): 1" in lines
    assert "Pagine candidate: 2; intervallo 1-3; buchi: 2" in lines


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
