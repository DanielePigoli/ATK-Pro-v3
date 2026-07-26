from __future__ import annotations

from pathlib import Path

import verify_mlol_dh_technical_probe as probe


def test_extract_candidates_finds_item_viewer_and_viewer_manifest():
    html = """
    <a href="https://arbor.medialibrary.it/item/185016bb-0d54-412f-9554-5eec348b09f0">item</a>
    <a href="https://viewers.medialibrary.it/mirador/index.html?manifest=https%3A%2F%2Farchiginnasio.jarvis.memooria.org%2Fmeta%2Fiiif%2F185016bb-0d54-412f-9554-5eec348b09f0%2Fmanifest">viewer</a>
    """

    candidates = probe.extract_candidates(html, "https://arbor.medialibrary.it/item/185016bb-0d54-412f-9554-5eec348b09f0")
    by_role = {candidate.role: candidate for candidate in candidates}

    assert by_role["mlol_item"].kind == "catalog_record"
    assert by_role["mlol_item"].identifier == "185016bb-0d54-412f-9554-5eec348b09f0"
    assert by_role["mirador_viewer"].kind == "viewer"
    assert by_role["viewer_manifest_parameter"].kind == "manifest"
    assert (
        by_role["viewer_manifest_parameter"].url
        == "https://archiginnasio.jarvis.memooria.org/meta/iiif/185016bb-0d54-412f-9554-5eec348b09f0/manifest"
    )


def test_extract_candidates_finds_relative_and_absolute_iiif_targets():
    html = """
    <a href="/iiif/185016bb-0d54-412f-9554-5eec348b09f0/manifest">manifest relativo</a>
    <a href="https://archiginnasio.jarvis.memooria.org/meta/iiif/185016bb-0d54-412f-9554-5eec348b09f0/manifest">manifest jarvis</a>
    <a href="https://archiginnasio.jarvis.memooria.org/meta/iiif/185016bb-0d54-412f-9554-5eec348b09f0/canvas/p1/info.json">info</a>
    <img src="https://archiginnasio.jarvis.memooria.org/meta/iiif/185016bb-0d54-412f-9554-5eec348b09f0/canvas/p1/full/1000,/0/default.jpg">
    """

    candidates = probe.extract_candidates(html, "https://arbor.medialibrary.it/item/185016bb-0d54-412f-9554-5eec348b09f0")
    kinds = {candidate.kind for candidate in candidates}
    roles = {candidate.role for candidate in candidates}

    assert {"manifest", "iiif_info", "image"} <= kinds
    assert "mlol_relative_manifest" in roles
    assert "jarvis_manifest" in roles
    assert "jarvis_info_json" in roles
    assert "iiif_content_image" in roles


def test_extract_candidates_marks_content_image_and_site_asset():
    html = """
    <img src="https://mlolassets.s3.eu-south-1.amazonaws.com/archiginnasio/185016bb-0d54-412f-9554-5eec348b09f0.jpg">
    <img src="/iiif/logo-iiif.png">
    <a href="https://arbor.medialibrary.it/item/185016bb-0d54-412f-9554-5eec348b09f0">item</a>
    <a href="https://arbor.medialibrary.it/item/185016bb-0d54-412f-9554-5eec348b09f0">duplicate</a>
    """

    candidates = probe.extract_candidates(html, "https://arbor.medialibrary.it/item/185016bb-0d54-412f-9554-5eec348b09f0")
    by_role = {candidate.role: candidate for candidate in candidates}

    assert by_role["content_image"].kind == "image"
    assert by_role["site_asset"].kind == "image"
    assert by_role["mlol_item"].kind == "catalog_record"
    assert len(candidates) == 3


def test_write_report_creates_csv(tmp_path: Path):
    report = tmp_path / "mlol_probe.csv"
    probe.write_report(
        report,
        [
            probe.ProbeCandidate(
                kind="manifest",
                role="jarvis_manifest",
                identifier="185016bb-0d54-412f-9554-5eec348b09f0",
                url="https://archiginnasio.jarvis.memooria.org/meta/iiif/185016bb-0d54-412f-9554-5eec348b09f0/manifest",
                source="html_attribute",
            )
        ],
    )

    text = report.read_text(encoding="utf-8")
    assert "kind,role,identifier,url,source" in text
    assert "jarvis_manifest" in text


def test_evaluate_readiness_requires_public_item_or_manifest():
    readiness = probe._evaluate_readiness([])

    assert readiness.startswith("GO/NO-GO: NO_GO")


def test_evaluate_readiness_holds_gallery_only_case():
    readiness = probe._evaluate_readiness(
        [
            probe.ProbeCandidate(
                kind="image",
                role="content_image",
                identifier="cover.jpg",
                url="https://mlolassets.s3.eu-south-1.amazonaws.com/example/cover.jpg",
                source="html_attribute",
            )
        ]
    )

    assert readiness.startswith("GO/NO-GO: HOLD")


def test_evaluate_readiness_marks_item_and_manifest_for_review():
    readiness = probe._evaluate_readiness(
        [
            probe.ProbeCandidate(
                kind="catalog_record",
                role="mlol_item",
                identifier="185016bb-0d54-412f-9554-5eec348b09f0",
                url="https://arbor.medialibrary.it/item/185016bb-0d54-412f-9554-5eec348b09f0",
                source="html_attribute",
            ),
            probe.ProbeCandidate(
                kind="manifest",
                role="jarvis_manifest",
                identifier="185016bb-0d54-412f-9554-5eec348b09f0",
                url="https://archiginnasio.jarvis.memooria.org/meta/iiif/185016bb-0d54-412f-9554-5eec348b09f0/manifest",
                source="html_attribute",
            ),
        ]
    )

    assert readiness.startswith("GO/NO-GO: REVIEW")
