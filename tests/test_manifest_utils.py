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
