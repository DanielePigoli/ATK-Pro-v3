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


def test_bdl_document_run_dispatches_all_multipage_canvases_to_register(monkeypatch, tmp_path):
    elab = Elaborazione(
        "D",
        BDL_PDF_URL,
        str(tmp_path),
        portale="biblioteca_digitale_lombarda",
    )
    canvases = _bdl_tiles() + [{
        "@id": "synthetic://biblioteca_digitale_lombarda/12404/canvas/2",
        "images": [{"resource": {"service": {"@id": "https://bdl.test/iiif/2/2"}}}],
    }]
    elab.manifest_path = None
    monkeypatch.setattr(elab, "_fetch_manifest", lambda: {
        "metadata": [],
        "sequences": [{"canvases": canvases}],
    })
    calls = []
    monkeypatch.setattr(elab, "_process_document", lambda tiles, metadata: False)
    monkeypatch.setattr(elab, "_process_register", lambda tiles, metadata: calls.append(tiles) or True)

    assert elab.run() is True
    assert calls == [canvases]

def test_bdl_empty_name_gets_stable_item_fallback(tmp_path):
    elab = Elaborazione(
        "D",
        BDL_PDF_URL,
        str(tmp_path),
        portale="biblioteca_digitale_lombarda",
    )

    elab.set_nome_file("")

    assert elab.nome_file == "BDL_12404"

def test_bdl_register_second_pass_retries_only_failed_placeholders(monkeypatch, tmp_path):
    from PIL import Image

    class FlakyAdapter:
        portal_label = "BDL"

        def __init__(self):
            self.calls = {}

        def download_image(self, url):
            self.calls[url] = self.calls.get(url, 0) + 1
            if "/iiif/2/2/" in url and self.calls[url] == 1:
                return None, 502, 0
            return Image.new("RGB", (4, 4), "red"), 200, 12

    urls = ["https://www.bdl.servizirl.it/cantaloupe/iiif/2/1/full/full/0/default.jpg",
            "https://www.bdl.servizirl.it/cantaloupe/iiif/2/2/full/full/0/default.jpg"]
    canvases = [
        {"label": f"Pagina {idx}", "images": [{"resource": {"@id": url, "service": {"@id": url.split("/full/")[0]}}}]}
        for idx, url in enumerate(urls, 1)
    ]
    adapter = FlakyAdapter()
    monkeypatch.setattr("src.elaborazione.resolve_direct_pdf_download", lambda *args, **kwargs: (None, None))
    monkeypatch.setattr("src.elaborazione.resolve_direct_image_download", lambda portal, canvas, service: (adapter, canvas["images"][0]["resource"]["@id"]))

    elab = Elaborazione("R", BDL_PDF_URL, str(tmp_path), portale="biblioteca_digitale_lombarda")
    elab.set_nome_file("BDL_12404")
    elab.formats = ["PDF"]
    elab.manifest = {"sequences": [{"canvases": canvases}]}
    generated = []
    monkeypatch.setattr(elab, "_generate_register_pdf", lambda names, image_dir=None: generated.extend(names) or str(tmp_path / "BDL_12404.pdf"))

    assert elab._process_register(canvases, {}) is True
    assert adapter.calls[urls[0]] == 1
    assert adapter.calls[urls[1]] == 2
    assert generated == ["BDL_12404_canvas_1_pdftmp.png", "BDL_12404_canvas_2_pdftmp.png"]