from pathlib import Path

from PIL import Image

from src.elaborazione import Elaborazione, _save_direct_image_outputs
from src.portal_adapters import ficlit_direct_image_url_from_canvas


def test_ficlit_direct_image_url_is_extracted_from_canvas():
    canvas = {
        "images": [
            {
                "resource": {
                    "@id": "https://dl.ficlit.unibo.it/iiif/2/45498/full/699,800/0/default.jpg",
                    "service": {
                        "@id": "https://dl.ficlit.unibo.it/iiif/2/45498",
                    },
                }
            }
        ]
    }

    assert (
        ficlit_direct_image_url_from_canvas(canvas)
        == "https://dl.ficlit.unibo.it/iiif/2/45498/full/699,800/0/default.jpg"
    )


def test_ficlit_direct_image_url_rejects_external_canvas():
    canvas = {
        "images": [
            {
                "resource": {
                    "@id": "https://example.test/iiif/2/45498/full/699,800/0/default.jpg",
                    "service": {
                        "@id": "https://dl.ficlit.unibo.it/iiif/2/45498",
                    },
                }
            }
        ]
    }

    assert ficlit_direct_image_url_from_canvas(canvas) is None


def test_save_direct_image_outputs_creates_pdf_and_cleans_temp(tmp_path, monkeypatch):
    image = Image.new("RGB", (12, 12), "white")

    saved_formats = []
    monkeypatch.setattr(
        "src.elaborazione.save_image_variants",
        lambda img, out, name, formats, meta=None: saved_formats.extend(formats),
    )

    pdf_calls = []

    def fake_create_pdf(input_dir, output_pdf):
        pdf_calls.append((input_dir, output_pdf))
        Path(output_pdf).write_bytes(b"%PDF-1.4\n%%EOF")
        return output_pdf

    monkeypatch.setattr("src.elaborazione.create_pdf_from_images", fake_create_pdf)

    _save_direct_image_outputs(image, str(tmp_path), "ficlit_test", ["PNG", "PDF"], meta={"x": "y"})

    assert saved_formats == ["PNG"]
    assert len(pdf_calls) == 1
    assert Path(pdf_calls[0][1]).name == "ficlit_test.pdf"
    assert not (tmp_path / "_tmp_pdf_images").exists()


def test_save_direct_image_outputs_defaults_to_image_formats(tmp_path, monkeypatch):
    image = Image.new("RGB", (12, 12), "white")

    saved_formats = []
    monkeypatch.setattr(
        "src.elaborazione.save_image_variants",
        lambda img, out, name, formats, meta=None: saved_formats.extend(formats),
    )
    monkeypatch.setattr(
        "src.elaborazione.create_pdf_from_images",
        lambda *args, **kwargs: (_ for _ in ()).throw(AssertionError("PDF non richiesto")),
    )

    _save_direct_image_outputs(image, str(tmp_path), "ficlit_test", [], meta=None)

    assert saved_formats == ["PNG", "JPEG", "TIFF"]
    assert not (tmp_path / "_tmp_pdf_images").exists()


def test_save_direct_document_outputs_reuses_shared_helper(tmp_path, monkeypatch):
    elab = Elaborazione(
        "D",
        "https://example.test/record/1",
        str(tmp_path),
        portale="manifest_diretto",
    )
    elab.nome_file = "Documento Test"

    calls = []

    def fake_save_direct(img, out_dir, base_name, formats, meta=None):
        calls.append((img, out_dir, base_name, formats, meta))
        return True

    monkeypatch.setattr("src.elaborazione._save_direct_image_outputs", fake_save_direct)

    image = Image.new("RGB", (12, 12), "white")
    canvas = {"label": "Pagina 1", "@id": "synthetic://canvas/1"}

    elab._save_direct_document_outputs(
        image,
        canvas,
        "https://example.test/image.jpg",
        ["PNG", "PDF"],
    )

    assert len(calls) == 1
    assert calls[0][1] == str(tmp_path)
    assert calls[0][2] == "Documento Test"
    assert calls[0][3] == ["PNG", "PDF"]
    assert calls[0][4]["Page"] == "Pagina 1"
