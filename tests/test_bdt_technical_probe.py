from __future__ import annotations

from pathlib import Path

import verify_bdt_technical_probe as probe


def test_extract_candidates_finds_public_bdt_asset_links():
    html = """
    <html>
      <a href="/iiif/123/manifest.json">manifest</a>
      <img src="/storage/image/page-0001.jpg">
      <a data-download="/download/documento.pdf">PDF</a>
      <script>
        const info = "https://bdt.bibcom.trento.it/iiif/123/page-1/info.json";
      </script>
    </html>
    """

    candidates = probe.extract_candidates(html, "https://bdt.bibcom.trento.it/Iconografia/4052")
    by_kind = {candidate.kind: candidate.url for candidate in candidates}

    assert by_kind["manifest"] == "https://bdt.bibcom.trento.it/iiif/123/manifest.json"
    assert by_kind["image"] == "https://bdt.bibcom.trento.it/storage/image/page-0001.jpg"
    assert by_kind["pdf"] == "https://bdt.bibcom.trento.it/download/documento.pdf"
    assert by_kind["iiif_info"] == "https://bdt.bibcom.trento.it/iiif/123/page-1/info.json"


def test_extract_candidates_ignores_duplicates_and_non_download_links():
    html = """
    <a href="#page/n0">anchor</a>
    <a href="mailto:info@example.test">mail</a>
    <img src="/storage/image/page-0001.jpg">
    <a href="/storage/image/page-0001.jpg">same image</a>
    """

    candidates = probe.extract_candidates(html, "https://bdt.bibcom.trento.it/Iconografia/4052")

    assert candidates == [
        probe.ProbeCandidate(
            kind="image",
            url="https://bdt.bibcom.trento.it/storage/image/page-0001.jpg",
            source="html_attribute",
        )
    ]


def test_write_report_creates_csv(tmp_path: Path):
    report = tmp_path / "bdt_probe.csv"
    probe.write_report(
        report,
        [
            probe.ProbeCandidate(
                kind="pdf",
                url="https://bdt.bibcom.trento.it/download/documento.pdf",
                source="html_attribute",
            )
        ],
    )

    assert "kind,url,source" in report.read_text(encoding="utf-8")
    assert "documento.pdf" in report.read_text(encoding="utf-8")
