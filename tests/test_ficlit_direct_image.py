from pathlib import Path

from PIL import Image

from src.elaborazione import (
    _ficlit_direct_image_url_from_canvas,
    _save_direct_image_outputs,
)


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
        _ficlit_direct_image_url_from_canvas(canvas)
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

    assert _ficlit_direct_image_url_from_canvas(canvas) is None


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
