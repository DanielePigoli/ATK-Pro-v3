from __future__ import annotations

from pathlib import Path

import verify_beic_technical_probe as probe


def test_extract_candidates_finds_beic_delivery_and_catalog_links():
    html = """
    <html>
      <a href="https://catalogue.beic.it/discovery/fulldisplay?docid=alma9925210904741&context=L&vid=39BEIC_INST:39BEIC_INST">record</a>
      <a href="https://preserver.beic.it/delivery/DeliveryManagerServlet?dps_pid=IE7400509">viewer</a>
      <a href="https://preserver.beic.it/delivery/DeliveryManagerServlet?dps_pid=IE4411197&select_viewer=metsViewer&dps_file=FL4412552">file</a>
    </html>
    """

    candidates = probe.extract_candidates(html, "https://digital.beic.it/")
    by_role = {candidate.role: candidate for candidate in candidates}

    assert by_role["primo_record"].kind == "catalog_record"
    assert by_role["primo_record"].identifier == "alma9925210904741"
    assert by_role["delivery_viewer"].kind == "beic_delivery"
    assert by_role["delivery_viewer"].identifier == "IE7400509"
    assert by_role["delivery_file"].kind == "beic_file"
    assert by_role["delivery_file"].identifier == "IE4411197"


def test_extract_candidates_finds_legacy_delivery_and_standard_assets():
    html = """
    <a href="https://gutenberg.beic.it/webclient/DeliveryManager?pid=3047747">legacy</a>
    <a href="/iiif/example/manifest.json">manifest</a>
    <a href="/iiif/example/page/info.json">info</a>
    <img src="/images/page-1.jpg">
    <a href="/download/item.pdf">pdf</a>
    """

    candidates = probe.extract_candidates(html, "https://digital.beic.it/item")
    kinds = {candidate.kind for candidate in candidates}
    roles = {candidate.role for candidate in candidates}

    assert "beic_delivery" in kinds
    assert "manifest" in kinds
    assert "iiif_info" in kinds
    assert "image" in kinds
    assert "pdf" in kinds
    assert "legacy_delivery_viewer" in roles


def test_extract_candidates_ignores_duplicates_and_non_download_links():
    html = """
    <a href="#content">anchor</a>
    <a href="mailto:info@example.test">mail</a>
    <a href="https://preserver.beic.it/delivery/DeliveryManagerServlet?dps_pid=IE7400509">viewer</a>
    <a href="https://preserver.beic.it/delivery/DeliveryManagerServlet?dps_pid=IE7400509">same viewer</a>
    """

    candidates = probe.extract_candidates(html, "https://digital.beic.it/")

    assert candidates == [
        probe.ProbeCandidate(
            kind="beic_delivery",
            role="delivery_viewer",
            url="https://preserver.beic.it/delivery/DeliveryManagerServlet?dps_pid=IE7400509",
            source="html_attribute",
            identifier="IE7400509",
        )
    ]


def test_write_report_creates_csv(tmp_path: Path):
    report = tmp_path / "beic_probe.csv"
    probe.write_report(
        report,
        [
            probe.ProbeCandidate(
                kind="beic_delivery",
                role="delivery_viewer",
                identifier="IE7400509",
                url="https://preserver.beic.it/delivery/DeliveryManagerServlet?dps_pid=IE7400509",
                source="html_attribute",
            )
        ],
    )

    text = report.read_text(encoding="utf-8")
    assert "kind,role,identifier,url,source" in text
    assert "IE7400509" in text
