import pytest
from pathlib import Path
from unittest.mock import patch
import requests
import json
import src.manifest_utils as mu
from src.manifest_utils import find_manifest_url, download_manifest

def test_find_manifest_url_con_manifest_json():
    class MockDriver:
        page_source = (
            "<html><body>"
            "<a href='https://dam-antenati.cultura.gov.it/antenati/containers/xyz789/manifest.json'>manifest</a>"
            "</body></html>"
        )
    result = find_manifest_url(MockDriver())
    assert result == "https://dam-antenati.cultura.gov.it/antenati/containers/xyz789/manifest.json"

def test_find_manifest_url_con_manifest_senza_json():
    class MockDriver:
        page_source = (
            "<html><body>"
            "<a href='https://dam-antenati.cultura.gov.it/antenati/containers/abc123/manifest'>manifest</a>"
            "</body></html>"
        )
    result = find_manifest_url(MockDriver())
    assert result == "https://dam-antenati.cultura.gov.it/antenati/containers/abc123/manifest"

def test_find_manifest_url_from_page_object():
    class FakePage:
        page_source = '<html><a href="manifest.json">m</a></html>'
    url = mu.find_manifest_url(FakePage())
    assert "manifest.json" in url


def test_extract_manifest_url_from_mirador_query():
    viewer_url = (
        "https://pm20.zbw.eu/mirador/"
        "?manifestId=https%3A%2F%2Fpm20.zbw.eu%2Fiiif%2Ffolder%2Fco%2F043177%2Fpublic.manifest.json"
        "&canvasId=https%3A%2F%2Fpm20.zbw.eu%2Fiiif%2Ffolder%2Fco%2F043177%2F00001%2F0001%2Fcanvas"
    )

    assert (
        mu.extract_manifest_url_from_viewer_url(viewer_url)
        == "https://pm20.zbw.eu/iiif/folder/co/043177/public.manifest.json"
    )


def test_get_manifest_builder_normalizes_portal_key():
    portale_key, builder = mu._get_manifest_builder("BUB-Digitale")

    assert portale_key == "bub_digitale"
    assert builder is mu._build_bub_digitale_manifest


def test_resolve_direct_manifest_url_returns_input_url():
    url = "https://example.test/iiif/manifest.json"

    assert mu._resolve_direct_manifest_url(url) == url
    assert mu.resolve_manifest_url(url, "manifest_diretto") == url


def test_resolve_standard_manifest_url_uses_builder():
    builder = lambda page_url: f"resolved::{page_url}"

    assert (
        mu._resolve_standard_manifest_url("https://example.test/item/1", builder)
        == "resolved::https://example.test/item/1"
    )
    assert mu._resolve_standard_manifest_url("https://example.test/item/1", None) is None


def test_robust_find_manifest_uses_viewer_query_without_fetch(monkeypatch):
    def fail_fetch(*_args, **_kwargs):
        raise AssertionError("robust_find_manifest should not fetch viewer URLs with manifestId")

    monkeypatch.setattr(mu, "_http_get", fail_fetch)
    url = mu.robust_find_manifest(
        "https://pm20.zbw.eu/mirador/?manifestId=https://pm20.zbw.eu/iiif/folder/co/043177/public.manifest.json"
    )

    assert url == "https://pm20.zbw.eu/iiif/folder/co/043177/public.manifest.json"


def test_resolve_bnc_roma_returns_synthetic_placeholder_without_empty_html_fetch():
    url = "http://digitale.bnc.roma.sbn.it/printedbooks/bncr_142624/bncr_142624_001"

    assert mu.resolve_manifest_url(url, "bnc_roma") == url


def test_resolve_biblioteca_digitale_siena_viewer_url():
    url = "https://bds.comune.siena.it/it/vieweriiif/?id=9917468302803300&type=sbn"

    assert (
        mu.resolve_manifest_url(url, "biblioteca_digitale_siena")
        == "https://bds.comune.siena.it/metadata/9917468302803300/manifest.json?type=sbn"
    )


def test_resolve_biblioteca_digitale_siena_defaults_to_sbn_type():
    url = "https://bds.comune.siena.it/it/vieweriiif/?id=9917468302803300"

    assert (
        mu.resolve_manifest_url(url, "biblioteca_digitale_siena")
        == "https://bds.comune.siena.it/metadata/9917468302803300/manifest.json?type=sbn"
    )


def test_resolve_bub_digitale_manifest_from_viewer_url():
    url = (
        "https://bub.unibo.it/it/bub-digitale/bollettini-parrocchiali/parola-di-vita"
        "?manifest=https%3A%2F%2Fbub.unibo.it%2Fiiif%2F2%2Fmanifest%2Fbub%2Fbollettiniparrocchiali%2F"
        "_castenaso_-_s_giovanni_battista%2Fjpg%2F1933.json&view=BookView"
    )

    assert (
        mu.resolve_manifest_url(url, "bub_digitale")
        == "https://bub.unibo.it/iiif/2/manifest/bub/bollettiniparrocchiali/_castenaso_-_s_giovanni_battista/jpg/1933.json"
    )


def test_resolve_bub_digitale_accepts_direct_manifest_url():
    url = "https://bub.unibo.it/iiif/2/manifest/bub/bollettiniparrocchiali/_castenaso_-_s_giovanni_battista/jpg/1933.json"

    assert mu.resolve_manifest_url(url, "bub_digitale") == url


def test_resolve_bub_digitale_rejects_non_bub_manifest_parameter():
    url = (
        "https://bub.unibo.it/it/bub-digitale/bollettini-parrocchiali/parola-di-vita"
        "?manifest=https%3A%2F%2Fexample.test%2Fmanifest.json&view=BookView"
    )

    assert mu.resolve_manifest_url(url, "bub_digitale") is None


def test_resolve_dl_ficlit_item_url_to_manifest():
    url = "https://dl.ficlit.unibo.it/s/lib/item/28429"

    assert mu.resolve_manifest_url(url, "dl_ficlit") == "https://dl.ficlit.unibo.it/iiif/2/28429/manifest"


def test_resolve_dl_ficlit_accepts_direct_manifest_url():
    url = "https://dl.ficlit.unibo.it/iiif/2/199245/manifest"

    assert mu.resolve_manifest_url(url, "dl_ficlit") == url


def test_resolve_dl_ficlit_rejects_non_ficlit_manifest_parameter():
    url = "https://dl.ficlit.unibo.it/s/lib/page/progetto?manifest=https%3A%2F%2Fexample.test%2Fmanifest"

    assert mu.resolve_manifest_url(url, "dl_ficlit") is None


def test_resolve_biblioteca_digitale_trentina_item_url():
    url = "https://bdt.bibcom.trento.it/Testi-a-stampa/113"

    assert mu.resolve_manifest_url(url, "biblioteca_digitale_trentina") == url


def test_build_biblioteca_digitale_trentina_synthetic_manifest_from_html():
    html = """
    <html>
      <title>BDT sample</title>
      <img src="/storage/images/10032-157-ita-IT/site_header_logo.png">
      <a href="/content/download/78214/1625910/file/BDT-113-TIf37.pdf">Scarica PDF</a>
      <img src="/storage/images/media/immagini-testi-a-stampa/page-1.jpg165/340889-1-ita-IT/page-1.jpg.jpg">
      <img src="/storage/images/media/immagini-testi-a-stampa/page-1.jpg165/340889-1-ita-IT/page-1.jpg_large.jpg">
      <img src="/storage/images/media/immagini-testi-a-stampa/page-2.jpg165/340893-1-ita-IT/page-2.jpg.jpg">
    </html>
    """

    manifest = mu.build_biblioteca_digitale_trentina_synthetic_manifest(
        "https://bdt.bibcom.trento.it/Testi-a-stampa/113",
        html=html,
    )

    assert manifest["@id"] == "synthetic://biblioteca_digitale_trentina/113"
    assert manifest["label"] == "BDT sample"
    assert manifest["seeAlso"][0]["@id"] == "https://bdt.bibcom.trento.it/content/download/78214/1625910/file/BDT-113-TIf37.pdf"

    canvases = manifest["sequences"][0]["canvases"]
    assert len(canvases) == 2
    assert canvases[0]["label"] == "Pagina 1"
    resource = canvases[0]["images"][0]["resource"]
    assert resource["@id"].endswith("page-1.jpg_large.jpg")
    assert resource["service"]["@context"] == "bdt_direct"
    assert canvases[1]["label"] == "Pagina 2"


def test_resolve_biblioteca_digitale_lombarda_pdf_url():
    url = "https://www.bdl.servizirl.it/bdl/public/rest/srv/item/12404/pdf"

    assert mu.resolve_manifest_url(url, "biblioteca_digitale_lombarda") == url


@patch("src.manifest_utils.requests.head")
def test_resolve_bncf_teca_manifest_uses_first_working_standard_url(mock_head, monkeypatch):
    class MockHeadResponse:
        ok = True

    mock_head.return_value = MockHeadResponse()
    monkeypatch.setattr(
        mu,
        "_build_bncf_teca_manifest",
        lambda _page_url: [
            "https://teca.bncf.firenze.sbn.it/iiif/manifest/one",
            "https://teca.bncf.firenze.sbn.it/iiif/manifest/two",
        ],
    )
    monkeypatch.setattr(
        mu,
        "build_bncf_teca_synthetic_manifest",
        lambda *_args, **_kwargs: {"@id": "synthetic://bncf/unused"},
    )

    assert (
        mu._resolve_bncf_teca_manifest("https://teca.bncf.firenze.sbn.it/viewer")
        == "https://teca.bncf.firenze.sbn.it/iiif/manifest/one"
    )


def test_build_biblioteca_digitale_lombarda_pdf_manifest():
    url = "https://www.bdl.servizirl.it/bdl/public/rest/srv/item/12404/pdf"

    manifest = mu.build_biblioteca_digitale_lombarda_pdf_manifest(url)

    assert manifest["@id"] == "synthetic://biblioteca_digitale_lombarda/12404"
    assert manifest["seeAlso"][0]["@id"] == url
    canvas = manifest["sequences"][0]["canvases"][0]
    resource = canvas["images"][0]["resource"]
    assert resource["format"] == "application/pdf"
    assert resource["service"]["@context"] == "bdl_direct_pdf"
    assert resource["service"]["pdf_url"] == url


def test_resolve_rovereto_item_url():
    url = "https://digitallibrary.bibliotecacivica.rovereto.tn.it/entities/publication/e4199e9b-c79b-4c3d-b157-be2dcfc0407f"

    assert mu.resolve_manifest_url(url, "rovereto_digital_library") == url


def test_build_rovereto_synthetic_manifest_from_dspace_api(monkeypatch):
    item_uuid = "e4199e9b-c79b-4c3d-b157-be2dcfc0407f"
    bundle_uuid = "6c76babc-df6f-41a7-9084-40279e01b800"
    page_1_uuid = "01882cb0-c7ad-4313-bede-363686111ffd"
    page_2_uuid = "04c14975-96bb-4751-ae01-3fb9ae2b9715"
    pdf_uuid = "14cb1a01-c300-4807-9c3d-a4531b1cb77b"
    license_uuid = "4ccfd300-65d8-419b-b1a4-0784d33a85be"
    cover_uuid = "ebd6b368-7fc7-4a54-933f-8874fd52adf0"
    text_uuid = "caeb8053-a73b-4c9d-b8e3-fd1bbca9cf39"
    base = "https://digitallibrary.bibliotecacivica.rovereto.tn.it"
    item_url = f"{base}/server/api/core/items/{item_uuid}"
    bundles_url = f"{item_url}/bundles"
    bundle_url = f"{base}/server/api/core/bundles/{bundle_uuid}"
    bitstreams_url = f"{bundle_url}/bitstreams"
    bitstreams_next_url = f"{bitstreams_url}?page=1"

    def bitstream(uuid, name, mimetype):
        return {
            "uuid": uuid,
            "name": name,
            "sizeBytes": 123,
            "format": {"mimetype": mimetype},
            "_links": {
                "content": {"href": f"{base}/server/api/core/bitstreams/{uuid}/content"},
            },
        }

    responses = {
        item_url: {
            "uuid": item_uuid,
            "name": "Rovereto sample",
            "_links": {"bundles": {"href": bundles_url}},
        },
        bundles_url: {
            "_embedded": {
                "bundles": [
                    {"uuid": bundle_uuid, "_links": {"bitstreams": {"href": bitstreams_url}}},
                ]
            }
        },
        bitstreams_url: {
            "_links": {"next": {"href": bitstreams_next_url}},
            "_embedded": {
                "bitstreams": [
                    bitstream(pdf_uuid, "book.pdf", "application/pdf"),
                    bitstream(license_uuid, "license.txt", "text/plain"),
                    bitstream(cover_uuid, "book.pdf.jpg", "image/jpeg"),
                    bitstream(text_uuid, "book.pdf.txt", "text/plain"),
                    bitstream(page_1_uuid, "iiifpdf-0.png", "image/png"),
                ]
            }
        },
        bitstreams_next_url: {
            "_embedded": {
                "bitstreams": [
                    bitstream(page_2_uuid, "iiifpdf-1.png", "image/png"),
                ]
            }
        },
    }

    monkeypatch.setattr(mu, "_rovereto_get_json", lambda url, timeout=25: responses.get(url))

    manifest = mu.build_rovereto_synthetic_manifest(
        f"{base}/entities/publication/{item_uuid}"
    )

    assert manifest["@id"] == f"synthetic://rovereto_digital_library/{item_uuid}"
    assert manifest["label"] == "Rovereto sample"
    assert manifest["seeAlso"][0]["@id"] == f"{base}/server/api/core/bitstreams/{pdf_uuid}/content"
    canvases = manifest["sequences"][0]["canvases"]
    assert [canvas["label"] for canvas in canvases] == ["Pagina 1", "Pagina 2"]
    assert canvases[0]["images"][0]["resource"]["service"]["@context"] == "rovereto_direct"
    assert canvases[0]["images"][0]["resource"]["service"]["page_number"] == 1
    assert canvases[0]["images"][0]["resource"]["@id"] == f"{base}/server/api/core/bitstreams/{page_1_uuid}/content"


@patch("src.manifest_utils.requests.get")
def test_bncf_synthetic_manifest_does_not_write_debug_xml_by_default(mock_get, tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    class MockResponse:
        ok = True
        status_code = 200
        text = (
            '<?xml version="1.0" encoding="UTF-8"?>'
            '<mx-libro:readBook xmlns:mx-libro="http://www.imageViewer.mx/schema/gestioneLibro">'
            '<mx-libro:immagini numImg="1">'
            '<immagine ID="BNCF0000000001" mx-libro:sequenza="1">'
            '<altezza>100</altezza><larghezza>100</larghezza>'
            '</immagine>'
            '</mx-libro:immagini>'
            '</mx-libro:readBook>'
        )

    mock_get.return_value = MockResponse()

    manifest = mu.build_bncf_teca_synthetic_manifest(
        "https://teca.bncf.firenze.sbn.it/ImageViewer/servlet/ImageViewer?idr=BNCF0000000000&azione=readBook",
        "",
    )

    assert manifest["sequences"][0]["canvases"]
    assert not (tmp_path / "bncf_xml_debug_fallback" / "bncf_xml_debug.xml").exists()


def _sample_v3_manifest():
    return {
        "@context": "http://iiif.io/api/presentation/3/context.json",
        "id": "https://example.org/manifest",
        "type": "Manifest",
        "label": {"en": ["Sample folder"]},
        "metadata": [
            {"label": {"en": ["Archive"]}, "value": {"en": ["ZBW"]}},
        ],
        "rights": "https://creativecommons.org/publicdomain/mark/1.0/",
        "items": [
            {
                "id": "https://example.org/canvas/1",
                "type": "Canvas",
                "label": {"none": ["Page 1"]},
                "width": 1200,
                "height": 1800,
                "items": [
                    {
                        "id": "https://example.org/canvas/1/page",
                        "type": "AnnotationPage",
                        "items": [
                            {
                                "id": "https://example.org/anno/1",
                                "type": "Annotation",
                                "motivation": "painting",
                                "target": "https://example.org/canvas/1",
                                "body": {
                                    "id": "https://example.org/iiif/image/full/full/0/default.jpg",
                                    "type": "Image",
                                    "format": "image/jpeg",
                                    "width": 1200,
                                    "height": 1800,
                                    "service": [
                                        {
                                            "id": "https://example.org/iiif/image",
                                            "type": "ImageService3",
                                            "profile": "level2",
                                        }
                                    ],
                                },
                            }
                        ],
                    }
                ],
            }
        ],
    }


def test_normalize_iiif_v3_manifest_for_processing():
    normalized = mu.normalize_iiif_manifest_for_processing(_sample_v3_manifest())

    assert normalized["@type"] == "sc:Manifest"
    assert normalized["label"] == "Sample folder"
    assert normalized["metadata"] == [{"label": "Archive", "value": "ZBW"}]
    assert normalized["rights"] == "https://creativecommons.org/publicdomain/mark/1.0/"
    assert normalized["_atk_normalized_from_iiif_v3"] is True

    canvas = normalized["sequences"][0]["canvases"][0]
    assert canvas["@id"] == "https://example.org/canvas/1"
    assert canvas["label"] == "Page 1"
    resource = canvas["images"][0]["resource"]
    assert resource["@id"] == "https://example.org/iiif/image/full/full/0/default.jpg"
    assert resource["service"][0]["@id"] == "https://example.org/iiif/image"
    assert resource["service"][0]["@type"] == "ImageService3"

def test_download_manifest_url_non_valido(tmp_path):
    result = download_manifest(
        "https://dam-antenati.cultura.gov.it/antenati/containers/INVALID/manifest",
        str(tmp_path),
        titolo_doc="test_doc"
    )
    assert result is None

@patch("src.manifest_utils.requests.get")
def test_download_manifest_url_valido(mock_get, tmp_path):
    class MockResponse:
        status_code = 200
        def json(self):
            return {"@context": "http://iiif.io/api/presentation/2/context.json"}
        def raise_for_status(self): pass
    mock_get.return_value = MockResponse()
    result = download_manifest(
        "https://dam-antenati.cultura.gov.it/antenati/containers/abc123/manifest",
        str(tmp_path),
        titolo_doc="test_doc"
    )
    assert result["@context"] == "http://iiif.io/api/presentation/2/context.json"
    files = list(Path(tmp_path).glob("*.json"))
    assert files and files[0].exists()


@patch("src.manifest_utils.requests.get")
def test_download_manifest_external_uses_neutral_headers_and_normalizes_v3(mock_get, tmp_path):
    class MockResponse:
        status_code = 200
        text = "{}"
        content = b"{}"

        def json(self):
            return _sample_v3_manifest()

        def raise_for_status(self):
            pass

    mock_get.return_value = MockResponse()

    result = download_manifest(
        "https://pm20.zbw.eu/iiif/folder/co/043177/public.manifest.json",
        str(tmp_path),
        titolo_doc="zbw_test",
    )

    headers = mock_get.call_args.kwargs["headers"]
    assert headers["Referer"] == "https://pm20.zbw.eu/"
    assert "Origin" not in headers
    assert result["_atk_normalized_from_iiif_v3"] is True
    assert result["sequences"][0]["canvases"][0]["images"][0]["resource"]["service"][0]["@id"] == "https://example.org/iiif/image"

@patch("src.manifest_utils.requests.get", side_effect=requests.exceptions.RequestException("Errore di rete"))
def test_download_manifest_eccezione(mock_get, tmp_path):
    result = download_manifest(
        "https://dam-antenati.cultura.gov.it/antenati/containers/abc123/manifest",
        str(tmp_path),
        titolo_doc="test_doc"
    )
    assert result is None

@patch("src.manifest_utils.requests.get")
def test_manifest_corrotto_v16(mock_get, tmp_path):
    """Gestione manifest corrotto/non decodificabile."""
    class MockResponse:
        status_code = 200
        def json(self): raise json.JSONDecodeError("Errore di parsing", "doc", 0)
        def raise_for_status(self): pass
    mock_get.return_value = MockResponse()
    result = download_manifest(
        "https://dam-antenati.cultura.gov.it/antenati/containers/abc123/manifest",
        str(tmp_path),
        titolo_doc="test_doc"
    )
    assert result is None

@patch("src.manifest_utils.requests.get")
def test_manifest_incompleto_v16(mock_get, tmp_path):
    """Gestione manifest incompleto: ritorna comunque il JSON."""
    class MockResponse:
        status_code = 200
        def json(self): return {"sequences": [{}]}
        def raise_for_status(self): pass
    mock_get.return_value = MockResponse()
    result = mu.download_manifest(
        "https://dam-antenati.cultura.gov.it/antenati/containers/abc123/manifest",
        str(tmp_path),
        titolo_doc="test_doc"
    )
    assert isinstance(result, dict)
    assert "sequences" in result
    files = list(Path(tmp_path).glob("*.json"))
    assert files and files[0].exists()

@patch("src.manifest_utils.requests.get")
def test_manifest_chiavi_inattese_v16(mock_get, tmp_path):
    """Gestione manifest con chiavi inattese."""
    class MockResponse:
        status_code = 200
        def json(self): return {"unexpected": "value"}
        def raise_for_status(self): pass
    mock_get.return_value = MockResponse()
    result = mu.download_manifest(
        "https://dam-antenati.cultura.gov.it/antenati/containers/abc123/manifest",
        str(tmp_path),
        titolo_doc="test_doc"
    )
    assert result is None or isinstance(result, dict)

@patch("src.manifest_utils.requests.get")
def test_manifest_vuoto_valido(mock_get, tmp_path):
    """Gestione manifest vuoto ma decodificabile."""
    class MockResponse:
        status_code = 200
        def json(self): return {}
        def raise_for_status(self): pass
    mock_get.return_value = MockResponse()
    result = mu.download_manifest(
        "https://dam-antenati.cultura.gov.it/antenati/containers/abc123/manifest",
        str(tmp_path),
        titolo_doc="test_doc"
    )
    assert result == {}
    files = list(Path(tmp_path).glob("*.json"))
    assert files and files[0].exists()
