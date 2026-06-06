from __future__ import annotations

from pathlib import Path

import verify_bdl_technical_probe as probe


def test_extract_candidates_finds_bdl_record_shortlink_and_pdf():
    html = """
    <html>
      <a href="https://www.bdl.servizirl.it/vufind/Record/BDL-OGGETTO-133442">record</a>
      <a href="https://www.bdl.servizirl.it/bdl/public/rest/srv/item/12404/shortlink">shortlink</a>
      <a href="https://www.bdl.servizirl.it/bdl/public/rest/srv/item/12404/pdf">pdf</a>
    </html>
    """

    candidates = probe.extract_candidates(html, "https://www.bdl.servizirl.it/")
    by_role = {candidate.role: candidate for candidate in candidates}

    assert by_role["vufind_record"].kind == "catalog_record"
    assert by_role["vufind_record"].identifier == "133442"
    assert by_role["item_shortlink"].kind == "shortlink"
    assert by_role["item_shortlink"].identifier == "12404"
    assert by_role["document_pdf"].kind == "pdf"
    assert by_role["document_pdf"].identifier == "12404"


def test_extract_candidates_finds_relative_links_and_assets():
    html = """
    <a href="/vufind/Record/BDL-OGGETTO-133442">record</a>
    <a href="/bdl/public/rest/srv/item/12404/pdf">pdf</a>
    <img src="/cover/page-1.jpg">
    <a href="/iiif/example/manifest.json">manifest</a>
    """

    candidates = probe.extract_candidates(html, "https://www.bdl.servizirl.it/vufind/Record/BDL-OGGETTO-133442")
    kinds = {candidate.kind for candidate in candidates}

    assert kinds == {"catalog_record", "pdf", "image", "manifest"}
    assert any(candidate.url == "https://www.bdl.servizirl.it/bdl/public/rest/srv/item/12404/pdf" for candidate in candidates)


def test_extract_candidates_ignores_duplicates_and_non_download_links():
    html = """
    <a href="#content">anchor</a>
    <a href="mailto:info@example.test">mail</a>
    <a href="/bdl/public/rest/srv/item/12404/pdf">pdf</a>
    <a href="/bdl/public/rest/srv/item/12404/pdf">same pdf</a>
    """

    candidates = probe.extract_candidates(html, "https://www.bdl.servizirl.it/")

    assert candidates == [
        probe.ProbeCandidate(
            kind="pdf",
            role="document_pdf",
            identifier="12404",
            url="https://www.bdl.servizirl.it/bdl/public/rest/srv/item/12404/pdf",
            source="html_attribute",
        )
    ]


def test_write_report_creates_csv(tmp_path: Path):
    report = tmp_path / "bdl_probe.csv"
    probe.write_report(
        report,
        [
            probe.ProbeCandidate(
                kind="pdf",
                role="document_pdf",
                identifier="12404",
                url="https://www.bdl.servizirl.it/bdl/public/rest/srv/item/12404/pdf",
                source="html_attribute",
            )
        ],
    )

    text = report.read_text(encoding="utf-8")
    assert "kind,role,identifier,url,source" in text
    assert "12404" in text
