from io import BytesIO
from pathlib import Path

from PIL import Image

from src.elaborazione import Elaborazione


def _png_bytes(color="blue"):
    buffer = BytesIO()
    Image.new("RGB", (6, 8), color).save(buffer, format="PNG")
    return buffer.getvalue()


def _direct_image_canvas(image_url="https://images.example.test/page-1.png"):
    return {
        "@id": "https://example.test/canvas/1",
        "label": "Pagina 1",
        "images": [{
            "resource": {
                "@id": image_url,
                "@type": "dctypes:Image",
                "format": "image/png",
                "width": 6,
                "height": 8,
            },
        }],
    }


def test_register_downloads_direct_image_without_iiif_service(monkeypatch, tmp_path):
    payload = _png_bytes()

    class Response:
        ok = True
        status_code = 200
        content = payload

    monkeypatch.setattr("src.portal_adapters.requests.get", lambda *args, **kwargs: Response())

    canvas = _direct_image_canvas()
    elab = Elaborazione("R", "https://example.test/manifest.json", str(tmp_path), portale="manifest_diretto")
    elab.set_nome_file("direct_v3")
    elab.formats = ["PNG", "PDF"]
    elab.manifest = {"sequences": [{"canvases": [canvas]}]}
    generated = []
    monkeypatch.setattr(
        elab,
        "_generate_register_pdf",
        lambda names, image_dir=None: generated.extend(names) or str(tmp_path / "direct_v3.pdf"),
    )

    assert elab._process_register([canvas], {}) is True
    with Image.open(tmp_path / "direct_v3_canvas_1.png") as output:
        assert output.size == (6, 8)
        assert output.getpixel((0, 0)) == (0, 0, 255)
    assert generated == ["direct_v3_canvas_1_pdftmp.png"]
    assert not (tmp_path / "_direct_v3_pdf_recovery_images").exists()


def test_register_returns_false_and_removes_empty_pdf_workspace_when_no_image_source(tmp_path):
    canvas = _direct_image_canvas("https://example.test/page-1.bin")
    canvas["images"][0]["resource"]["format"] = "application/octet-stream"

    elab = Elaborazione("R", "https://example.test/manifest.json", str(tmp_path), portale="manifest_diretto")
    elab.set_nome_file("missing_direct")
    elab.formats = ["PNG", "PDF"]
    elab.manifest = {"sequences": [{"canvases": [canvas]}]}

    assert elab._process_register([canvas], {}) is False
    assert not list(Path(tmp_path).glob("*.png"))
    assert not (tmp_path / "_tmp_pdf_images").exists()
    assert not (tmp_path / "_missing_direct_pdf_recovery_images").exists()
    assert not (tmp_path / "missing_direct").exists()
