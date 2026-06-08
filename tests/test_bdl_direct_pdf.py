# -*- coding: utf-8 -*-

from pathlib import Path

from src.elaborazione import Elaborazione


BDL_PDF_URL = "https://www.bdl.servizirl.it/bdl/public/rest/srv/item/12404/pdf"


class FakePdfResponse:
    ok = True
    status_code = 200
    headers = {"Content-Type": "application/pdf"}
    content = b"%PDF-1.4\n% BDL test\n%%EOF"


def _bdl_tiles():
    return [{
        "@id": "synthetic://biblioteca_digitale_lombarda/12404/canvas/1",
        "label": "PDF diretto",
        "images": [{
            "resource": {
                "@id": BDL_PDF_URL,
                "service": {
                    "@context": "bdl_direct_pdf",
                    "@id": BDL_PDF_URL,
                    "pdf_url": BDL_PDF_URL,
                },
            },
        }],
    }]


def test_bdl_document_only_pdf_uses_direct_pdf(monkeypatch, tmp_path):
    calls = []

    def fake_get(url, **kwargs):
        calls.append((url, kwargs))
        return FakePdfResponse()

    monkeypatch.setattr("src.elaborazione.requests.get", fake_get)
    elab = Elaborazione(
        "D",
        BDL_PDF_URL,
        str(tmp_path),
        portale="biblioteca_digitale_lombarda",
    )
    elab.nome_file = "BDL Test"
    elab.formats = ["PDF"]
    elab.manifest = {
        "seeAlso": [{"@id": BDL_PDF_URL, "format": "application/pdf"}],
        "sequences": [{"canvases": _bdl_tiles()}],
    }

    assert elab._process_document(_bdl_tiles(), {}) is True
    assert calls[0][0] == BDL_PDF_URL
    assert calls[0][1]["headers"]["Referer"] == "https://www.bdl.servizirl.it/"
    assert Path(tmp_path, "BDL_Test.pdf").read_bytes() == FakePdfResponse.content
    assert not Path(tmp_path, "_tmp_pdf_images").exists()


def test_bdl_document_with_image_format_is_not_supported(tmp_path):
    elab = Elaborazione(
        "D",
        BDL_PDF_URL,
        str(tmp_path),
        portale="biblioteca_digitale_lombarda",
    )
    elab.nome_file = "BDL Test"
    elab.formats = ["PDF", "PNG"]
    elab.manifest = {"sequences": [{"canvases": _bdl_tiles()}]}

    assert elab._process_document(_bdl_tiles(), {}) is False
