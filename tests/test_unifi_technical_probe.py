from __future__ import annotations

from pathlib import Path

import verify_unifi_technical_probe as probe


def test_extract_candidates_finds_item_entity_and_api_links():
    html = """
    <a href="https://improntedigitali.unifi.it/items/ea8510d3-4f09-41b6-b69a-5c4ff3d0d082">item</a>
    <a href="/entities/journalfile/ea8510d3-4f09-41b6-b69a-5c4ff3d0d082">entity</a>
    <a href="/server/api/core/items/ea8510d3-4f09-41b6-b69a-5c4ff3d0d082">api item</a>
    <a href="/server/api/core/items/ea8510d3-4f09-41b6-b69a-5c4ff3d0d082/thumbnail">thumb</a>
    """

    candidates = probe.extract_candidates(html, "https://improntedigitali.unifi.it/items/ea8510d3-4f09-41b6-b69a-5c4ff3d0d082")
    by_role = {candidate.role: candidate for candidate in candidates}

    assert by_role["unifi_item"].kind == "catalog_record"
    assert by_role["unifi_item"].identifier == "ea8510d3-4f09-41b6-b69a-5c4ff3d0d082"
    assert by_role["unifi_journalfile"].kind == "entity"
    assert by_role["unifi_rest_item"].kind == "api_item"
    assert by_role["unifi_item_thumbnail"].kind == "api_item"


def test_extract_candidates_finds_bundles_bitstreams_and_public_image():
    html = """
    <a href="/server/api/core/bundles/7d5cabc9-83e7-4659-a30b-bb42bbd47ab5/bitstreams">bundle bitstreams</a>
    <a href="/server/api/core/bitstreams/55463a6e-8496-483f-bdda-c12b6f51c965/content">thumb content</a>
    <a href="/server/api/core/bitstreams/55463a6e-8496-483f-bdda-c12b6f51c965/thumbnail">nested thumb</a>
    <img src="/assets/images/mirador-logo.svg">
    <img src="https://improntedigitali.unifi.it/iiif-thumb.jpg">
    """

    candidates = probe.extract_candidates(html, "https://improntedigitali.unifi.it/items/ea8510d3-4f09-41b6-b69a-5c4ff3d0d082")
    roles = {candidate.role for candidate in candidates}

    assert "unifi_bundle_bitstreams" in roles
    assert "unifi_bitstream_content" in roles
    assert "unifi_bitstream_thumbnail" in roles
    assert "mirador_brand_asset" in roles
    assert "public_image" in roles


def test_extract_candidates_finds_viewer_manifest_and_info_json():
    html = """
    <a href="/viewer?manifest=https%3A%2F%2Fimprontedigitali.unifi.it%2Fiiif%2F2%2Fmanifest%2Fea8510d3-4f09-41b6-b69a-5c4ff3d0d082.json">viewer</a>
    <a href="https://improntedigitali.unifi.it/iiif/2/manifest/ea8510d3-4f09-41b6-b69a-5c4ff3d0d082.json">manifest</a>
    <a href="/iiif/2/ea8510d3-4f09-41b6-b69a-5c4ff3d0d082/canvas/p1/info.json">info</a>
    """

    candidates = probe.extract_candidates(html, "https://improntedigitali.unifi.it/items/ea8510d3-4f09-41b6-b69a-5c4ff3d0d082")
    by_role = {candidate.role: candidate for candidate in candidates}

    assert by_role["unifi_viewer_manifest_parameter"].kind == "viewer"
    assert by_role["unifi_iiif_manifest"].kind == "manifest"
    assert by_role["unifi_iiif_info"].kind == "iiif_info"


def test_extract_candidates_ignores_duplicates_and_external_urls():
    html = """
    <a href="/items/ea8510d3-4f09-41b6-b69a-5c4ff3d0d082">item 1</a>
    <a href="/items/ea8510d3-4f09-41b6-b69a-5c4ff3d0d082">item 2</a>
    <a href="mailto:info@example.test">mail</a>
    <a href="https://example.test/server/api/core/items/ea8510d3-4f09-41b6-b69a-5c4ff3d0d082">external</a>
    """

    candidates = probe.extract_candidates(html, "https://improntedigitali.unifi.it/")

    assert len(candidates) == 1
    assert candidates[0].role == "unifi_item"


def test_write_report_creates_csv(tmp_path: Path):
    report = tmp_path / "unifi_probe.csv"
    probe.write_report(
        report,
        [
            probe.ProbeCandidate(
                kind="api_item",
                role="unifi_rest_item",
                identifier="ea8510d3-4f09-41b6-b69a-5c4ff3d0d082",
                url="https://improntedigitali.unifi.it/server/api/core/items/ea8510d3-4f09-41b6-b69a-5c4ff3d0d082",
                source="html_attribute",
            )
        ],
    )

    text = report.read_text(encoding="utf-8")
    assert "kind,role,identifier,url,source" in text
    assert "unifi_rest_item" in text


def test_evaluate_readiness_distinguishes_review_from_hold():
    review = probe._evaluate_readiness(
        [
            probe.ProbeCandidate("catalog_record", "unifi_item", "id", "https://improntedigitali.unifi.it/items/id", "input_url"),
            probe.ProbeCandidate("api_item", "unifi_rest_item", "id", "https://improntedigitali.unifi.it/server/api/core/items/id", "html_attribute"),
            probe.ProbeCandidate("api_item", "unifi_item_thumbnail", "id", "https://improntedigitali.unifi.it/server/api/core/items/id/thumbnail", "html_attribute"),
            probe.ProbeCandidate("bundle", "unifi_bundle_bitstreams", "bundle", "https://improntedigitali.unifi.it/server/api/core/bundles/bundle/bitstreams", "html_attribute"),
        ]
    )
    hold = probe._evaluate_readiness(
        [
            probe.ProbeCandidate("catalog_record", "unifi_item", "id", "https://improntedigitali.unifi.it/items/id", "input_url"),
            probe.ProbeCandidate("api_item", "unifi_rest_item", "id", "https://improntedigitali.unifi.it/server/api/core/items/id", "html_attribute"),
        ]
    )

    assert review.startswith("GO/NO-GO: REVIEW")
    assert hold.startswith("GO/NO-GO: HOLD")


def test_evaluate_readiness_marks_viewer_iiif_signals_for_review():
    review = probe._evaluate_readiness(
        [
            probe.ProbeCandidate("catalog_record", "unifi_item", "id", "https://improntedigitali.unifi.it/items/id", "input_url"),
            probe.ProbeCandidate("api_item", "unifi_rest_item", "id", "https://improntedigitali.unifi.it/server/api/core/items/id", "html_attribute"),
            probe.ProbeCandidate("bundle", "unifi_bundle_bitstreams", "bundle", "https://improntedigitali.unifi.it/server/api/core/bundles/bundle/bitstreams", "html_attribute"),
            probe.ProbeCandidate("manifest", "unifi_iiif_manifest", "manifest.json", "https://improntedigitali.unifi.it/iiif/2/manifest/id.json", "html_attribute"),
        ]
    )

    assert "viewer/IIIF" in review
