from __future__ import annotations

from pathlib import Path

import verify_phaidra_technical_probe as probe


def test_extract_candidates_finds_object_manifest_and_metadata_exports():
    html = """
    <a href="https://phaidra.cab.unipd.it/view/o:369506">scheda</a>
    <a href="https://phaidra.unipd.it/api/object/o:369506/iiifmanifest">IIIF-MANIFEST</a>
    <a href="https://phaidra.unipd.it/api/object/o:369506/uwmetadata?format=xml">Metadati XML</a>
    <a href="https://phaidra.unipd.it/api/object/o:369506/index/dc">Dublin Core</a>
    """

    candidates = probe.extract_candidates(html, "https://phaidra.cab.unipd.it/view/o:369506")
    by_role = {candidate.role: candidate for candidate in candidates}

    assert by_role["phaidra_object_page"].kind == "catalog_record"
    assert by_role["phaidra_object_page"].identifier == "o:369506"
    assert by_role["phaidra_iiif_manifest"].kind == "manifest"
    assert by_role["phaidra_metadata_export"].kind == "metadata_export"


def test_extract_candidates_finds_iiif_image_thumbnail_and_download():
    html = """
    <img src="https://phaidra.unipd.it/api/object/o:369506/thumbnail">
    <a href="https://phaidra.unipd.it/api/object/o:369506/download">download</a>
    <a href="https://phaidra.unipd.it/detail/o:369506.download">download alt</a>
    <img src="https://phaidra.unipd.it/api/imageserver?IIIF=o:369507.tif/full/full/0/default.jpg">
    <a href="https://phaidra.unipd.it/api/imageserver?IIIF=o:369507.tif/info.json">info</a>
    """

    candidates = probe.extract_candidates(html, "https://phaidra.cab.unipd.it/view/o:369506")
    by_role = {candidate.role: candidate for candidate in candidates}

    assert by_role["phaidra_thumbnail"].kind == "image"
    assert by_role["phaidra_download"].kind == "pdf"
    assert by_role["iiif_content_image"].kind == "image"
    assert by_role["phaidra_info_json"].kind == "iiif_info"


def test_extract_candidates_does_not_treat_detail_download_as_object_page():
    html = """
    <a href="https://phaidra.unipd.it/detail/o:369506.download">download alt</a>
    <a href="https://phaidra.cab.unipd.it/view/o:369506">scheda</a>
    """

    candidates = probe.extract_candidates(html, "https://phaidra.cab.unipd.it/view/o:369506")

    assert candidates == [
        probe.ProbeCandidate(
            kind="catalog_record",
            role="phaidra_object_page",
            identifier="o:369506",
            url="https://phaidra.cab.unipd.it/view/o:369506",
            source="html_attribute",
        ),
        probe.ProbeCandidate(
            kind="pdf",
            role="phaidra_download",
            identifier="o:369506",
            url="https://phaidra.unipd.it/detail/o:369506.download",
            source="html_attribute",
        ),
    ]


def test_extract_candidates_ignores_duplicates():
    html = """
    <a href="https://phaidra.unipd.it/api/object/o:369506/iiifmanifest">manifest</a>
    <a href="https://phaidra.unipd.it/api/object/o:369506/iiifmanifest">manifest duplicate</a>
    """

    candidates = probe.extract_candidates(html, "https://phaidra.cab.unipd.it/view/o:369506")

    assert candidates == [
        probe.ProbeCandidate(
            kind="manifest",
            role="phaidra_iiif_manifest",
            identifier="o:369506",
            url="https://phaidra.unipd.it/api/object/o:369506/iiifmanifest",
            source="html_attribute",
        )
    ]


def test_write_report_creates_csv(tmp_path: Path):
    report = tmp_path / "phaidra_probe.csv"
    probe.write_report(
        report,
        [
            probe.ProbeCandidate(
                kind="manifest",
                role="phaidra_iiif_manifest",
                identifier="o:369506",
                url="https://phaidra.unipd.it/api/object/o:369506/iiifmanifest",
                source="html_attribute",
            )
        ],
    )

    text = report.read_text(encoding="utf-8")
    assert "kind,role,identifier,url,source" in text
    assert "phaidra_iiif_manifest" in text
