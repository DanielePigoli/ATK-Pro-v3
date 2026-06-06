# -*- coding: utf-8 -*-

from pathlib import Path

from src.elaborazione import Elaborazione


BDT_PDF_URL = "https://bdt.bibcom.trento.it/content/download/78214/1625910/file/BDT-113-TIf37.pdf"
BDT_IMAGE_URL = (
    "https://s3-eu-west-1.amazonaws.com/static.comunitatrentina.it/"
    "var/trentoarchiviobiblioteca/storage/images/media/immagini-testi-a-stampa/"
    "page-1.jpg165/340889-1-ita-IT/page-1.jpg_large.jpg"
)


class FakePdfResponse:
    ok = True
    status_code = 200
    headers = {"Content-Type": "application/pdf"}
    content = b"%PDF-1.4\n% BDT test\n%%EOF"


def _bdt_tiles():
    return [{
        "@id": "synthetic://biblioteca_digitale_trentina/113/canvas/1",
        "label": "Pagina 1",
        "images": [{
            "resource": {
                "@id": BDT_IMAGE_URL,
                "service": {
                    "@context": "bdt_direct",
                    "@id": BDT_IMAGE_URL,
                    "pdf_url": BDT_PDF_URL,
                },
            },
        }],
    }]


def _make_bdt_elab(record_type, tmp_path):
    elab = Elaborazione(
        record_type,
        "https://bdt.bibcom.trento.it/Testi-a-stampa/113",
        str(tmp_path),
        portale="biblioteca_digitale_trentina",
    )
    elab.nome_file = "BDT Test"
    elab.formats = ["PDF"]
    elab.manifest = {
        "seeAlso": [{"@id": BDT_PDF_URL, "format": "application/pdf"}],
        "sequences": [{"canvases": _bdt_tiles()}],
    }
    return elab


def test_bdt_document_only_pdf_uses_direct_pdf(monkeypatch, tmp_path):
    calls = []

    def fake_get(url, **kwargs):
        calls.append((url, kwargs))
        return FakePdfResponse()

    monkeypatch.setattr("src.elaborazione.requests.get", fake_get)
    elab = _make_bdt_elab("D", tmp_path)

    assert elab._process_document(_bdt_tiles(), {}) is True
    assert calls[0][0] == BDT_PDF_URL
    assert calls[0][1]["headers"]["Referer"] == "https://bdt.bibcom.trento.it/"
    assert Path(tmp_path, "BDT_Test.pdf").read_bytes() == FakePdfResponse.content
    assert not Path(tmp_path, "_tmp_pdf_images").exists()


def test_bdt_register_only_pdf_uses_direct_pdf(monkeypatch, tmp_path):
    calls = []

    def fake_get(url, **kwargs):
        calls.append((url, kwargs))
        return FakePdfResponse()

    monkeypatch.setattr("src.elaborazione.requests.get", fake_get)
    elab = _make_bdt_elab("R", tmp_path)

    assert elab._process_register(_bdt_tiles(), {}) is True
    assert calls[0][0] == BDT_PDF_URL
    assert Path(tmp_path, "BDT_Test.pdf").read_bytes() == FakePdfResponse.content
    assert not Path(tmp_path, "_tmp_pdf_images").exists()
