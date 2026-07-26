from __future__ import annotations

from pathlib import Path

import verify_doge_technical_probe as probe


def test_extract_candidates_finds_entity_handle_and_api_links():
    html = """
    <a href="https://doge.unige.net/entities/publication/b1c2be2c-e1ae-4676-93e3-07e8e8398f72">item</a>
    <a href="/handle/20.500.12732/421">handle</a>
    <a href="/server/api/core/items/b1c2be2c-e1ae-4676-93e3-07e8e8398f72">api item</a>
    <a href="/server/api/core/items/b1c2be2c-e1ae-4676-93e3-07e8e8398f72/thumbnail">thumb</a>
    """

    candidates = probe.extract_candidates(html, "https://doge.unige.net/entities/publication/b1c2be2c-e1ae-4676-93e3-07e8e8398f72")
    by_role = {candidate.role: candidate for candidate in candidates}

    assert by_role["doge_publication"].kind == "catalog_record"
    assert by_role["doge_handle"].kind == "handle"
    assert by_role["doge_rest_item"].kind == "api_item"
    assert by_role["doge_item_thumbnail"].kind == "api_item"


def test_extract_candidates_finds_bundles_bitstreams_and_preview_assets():
    html = """
    <a href="/server/api/core/bundles/191a7a20-cd1b-484e-b585-8700feb4a7c2/bitstreams">bundle bitstreams</a>
    <a href="/server/api/core/bitstreams/009bef47-3884-49cb-910b-107b281569ef/content">thumb content</a>
    <a href="/server/api/core/bitstreams/009bef47-3884-49cb-910b-107b281569ef/thumbnail">nested thumb</a>
    <img src="/assets/images/mirador-logo.svg">
    <img src="https://doge.unige.net/preview.jpg">
    """

    candidates = probe.extract_candidates(html, "https://doge.unige.net/entities/publication/b1c2be2c-e1ae-4676-93e3-07e8e8398f72")
    roles = {candidate.role for candidate in candidates}

    assert "doge_bundle_bitstreams" in roles
    assert "doge_bitstream_content" in roles
    assert "doge_bitstream_thumbnail" in roles
    assert "mirador_brand_asset" in roles
    assert "public_image" in roles


def test_extract_candidates_ignores_duplicates_and_external_urls():
    html = """
    <a href="/handle/20.500.12732/421">handle 1</a>
    <a href="/handle/20.500.12732/421">handle 2</a>
    <a href="mailto:info@example.test">mail</a>
    <a href="https://example.test/server/api/core/items/b1c2be2c-e1ae-4676-93e3-07e8e8398f72">external</a>
    """

    candidates = probe.extract_candidates(html, "https://doge.unige.net/")

    assert len(candidates) == 1
    assert candidates[0].role == "doge_handle"


def test_write_report_creates_csv(tmp_path: Path):
    report = tmp_path / "doge_probe.csv"
    probe.write_report(
        report,
        [
            probe.ProbeCandidate(
                kind="api_item",
                role="doge_rest_item",
                identifier="b1c2be2c-e1ae-4676-93e3-07e8e8398f72",
                url="https://doge.unige.net/server/api/core/items/b1c2be2c-e1ae-4676-93e3-07e8e8398f72",
                source="html_attribute",
            )
        ],
    )

    text = report.read_text(encoding="utf-8")
    assert "kind,role,identifier,url,source" in text
    assert "doge_rest_item" in text


def test_evaluate_readiness_returns_review_for_public_record_api_and_surrogates():
    result = probe._evaluate_readiness(
        [
            probe.ProbeCandidate("catalog_record", "doge_publication", "id", "https://doge.unige.net/entities/publication/id", "input_url"),
            probe.ProbeCandidate("api_item", "doge_rest_item", "id", "https://doge.unige.net/server/api/core/items/id", "html_attribute"),
            probe.ProbeCandidate("api_item", "doge_item_thumbnail", "id", "https://doge.unige.net/server/api/core/items/id/thumbnail", "html_attribute"),
            probe.ProbeCandidate("bundle", "doge_bundle_bitstreams", "bundle", "https://doge.unige.net/server/api/core/bundles/123/bitstreams", "html_attribute"),
            probe.ProbeCandidate("bitstream", "doge_bitstream_content", "bit", "https://doge.unige.net/server/api/core/bitstreams/bit/content", "html_attribute"),
        ]
    )

    assert result.startswith("GO/NO-GO: REVIEW")
