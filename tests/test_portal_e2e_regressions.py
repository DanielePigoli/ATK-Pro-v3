from pathlib import Path

from PIL import Image
from pypdf import PdfReader

from src.elaborazione import Elaborazione, _save_direct_image_outputs


def _bncf_canvas():
    image_url = (
        "https://teca.bncf.firenze.sbn.it/ImageViewer/servlet/ImageViewer"
        "?idr=BNCF00004140910&azione=showImg&sequence=1&reduce=0"
    )
    return {
        "@id": "canvas-BNCF00004140910",
        "label": "Pagina 1",
        "images": [{
            "resource": {
                "@id": image_url,
                "format": "image/jpeg",
                "service": {"@id": image_url},
            }
        }],
    }


def test_direct_document_outputs_create_real_pdf_and_remove_temp(tmp_path):
    image = Image.new("RGB", (20, 30), "white")

    _save_direct_image_outputs(
        image,
        str(tmp_path),
        "documento_diretto",
        ["PNG", "PDF"],
    )

    assert (tmp_path / "documento_diretto.png").is_file()
    pdf_path = tmp_path / "documento_diretto.pdf"
    assert len(PdfReader(str(pdf_path)).pages) == 1
    assert not (tmp_path / "_tmp_pdf_images").exists()


def test_bncf_document_uses_direct_image_adapter(monkeypatch, tmp_path):
    class FakeBncfAdapter:
        portal_label = "BNCF"

        def download_image(self, image_url):
            return Image.new("RGB", (20, 30), "white"), 200, 100

    canvas = _bncf_canvas()
    image_url = canvas["images"][0]["resource"]["@id"]
    monkeypatch.setattr(
        "src.elaborazione.resolve_direct_image_download",
        lambda *args, **kwargs: (FakeBncfAdapter(), image_url),
    )
    monkeypatch.setattr(
        "src.elaborazione.resolve_direct_pdf_download",
        lambda *args, **kwargs: (None, None),
    )

    elaboration = Elaborazione(
        "D",
        "https://teca.bncf.firenze.sbn.it/ImageViewer/servlet/ImageViewer"
        "?idr=BNCF00004140909&azione=readBook",
        str(tmp_path),
        portale="bncf_teca",
    )
    elaboration.set_nome_file("BNCF Test")
    elaboration.formats = ["PNG", "PDF"]
    elaboration.manifest = {"sequences": [{"canvases": [canvas]}]}

    assert elaboration._process_document([canvas], {}) is True
    assert (tmp_path / "BNCF Test.png").is_file()
    assert len(PdfReader(str(tmp_path / "BNCF Test.pdf")).pages) == 1
    assert not (tmp_path / "_tmp_pdf_images").exists()


def test_fetch_manifest_sanitizes_phaidra_remote_identifier(monkeypatch, tmp_path):
    manifest_url = "https://phaidra.unipd.it/api/object/o:327971/iiifmanifest"
    manifest = {"sequences": [{"canvases": [{}]}]}
    elaboration = Elaborazione(
        "R",
        "https://phaidra.cab.unipd.it/view/o:327971",
        str(tmp_path),
        portale="phaidra_unipd",
    )
    elaboration.set_nome_file("PHAIDRA Test")
    elaboration.formats = ["PNG", "PDF"]

    monkeypatch.setattr(elaboration, "_get_manifest_url", lambda: manifest_url)
    monkeypatch.setattr(
        "src.elaborazione.download_manifest",
        lambda *args, **kwargs: manifest,
    )

    assert elaboration._fetch_manifest() == manifest
    assert "o_327971" in Path(elaboration.manifest_path).name
    assert ":" not in Path(elaboration.manifest_path).name


def test_phaidra_document_uses_single_full_canvas_image(monkeypatch, tmp_path):
    image_url = (
        "https://phaidra.unipd.it/api/imageserver"
        "?IIIF=o:327971.tif/full/full/0/default.jpg"
    )
    service_url = "https://phaidra.unipd.it/api/imageserver?IIIF=o:327971.tif"
    canvas = {
        "@id": "https://phaidra.unipd.it/api/object/o:327971/canvas/1",
        "label": "Pagina 1",
        "images": [{
            "resource": {
                "@id": image_url,
                "format": "image/jpeg",
                "service": {"@id": service_url},
            }
        }],
    }
    seen = []

    class FakePhaidraAdapter:
        portal_label = "PHAIDRA"

        def download_image(self, requested_url):
            seen.append(requested_url)
            return Image.new("RGB", (20, 30), "white"), 200, 100

    monkeypatch.setattr(
        "src.elaborazione.resolve_direct_image_download",
        lambda *args, **kwargs: (FakePhaidraAdapter(), image_url),
    )
    monkeypatch.setattr(
        "src.elaborazione.resolve_direct_pdf_download",
        lambda *args, **kwargs: (None, None),
    )
    monkeypatch.setattr(
        "src.elaborazione.download_info_json",
        lambda *args, **kwargs: (_ for _ in ()).throw(
            AssertionError("PHAIDRA must not start a tile download")
        ),
    )

    elaboration = Elaborazione(
        "D",
        "https://phaidra.cab.unipd.it/view/o:327971",
        str(tmp_path),
        portale="phaidra_unipd",
    )
    elaboration.set_nome_file("PHAIDRA Test")
    elaboration.formats = ["PNG", "PDF"]
    elaboration.manifest = {"sequences": [{"canvases": [canvas]}]}

    assert elaboration._process_document([canvas], {}) is True
    assert seen == [image_url]
    assert (tmp_path / "PHAIDRA Test.png").is_file()
    assert len(PdfReader(str(tmp_path / "PHAIDRA Test.pdf")).pages) == 1
    assert not (tmp_path / "tiles_doc").exists()


def test_fetch_manifest_sanitizes_internetculturale_synthetic_identifier(
    monkeypatch,
    tmp_path,
):
    page_url = (
        "https://www.internetculturale.it/jmms/iccuviewer/"
        "iccu.jsp?id=oai:www.internetculturale.sbn.it/Teca:20:NT0000"
    )
    manifest = {"sequences": [{"canvases": [{}]}]}
    captured = {}

    class FakeSyntheticAdapter:
        portal_label = "InternetCulturale"

    def fake_resolve(portal_key, url, *, container_id, title_slug, scraped_html):
        captured["container_id"] = container_id
        return (
            FakeSyntheticAdapter(),
            manifest,
            f"manifest_{container_id}_{title_slug}.json",
        )

    elaboration = Elaborazione(
        "R",
        page_url,
        str(tmp_path),
        portale="internetculturale_estense",
    )
    elaboration.set_nome_file("Internet Culturale Test")
    elaboration.formats = ["PNG", "PDF"]
    monkeypatch.setattr(elaboration, "_get_manifest_url", lambda: page_url)
    monkeypatch.setattr(
        "src.elaborazione.resolve_synthetic_manifest_download",
        fake_resolve,
    )

    assert elaboration._fetch_manifest() == manifest
    assert captured["container_id"] == "iccu.jsp_id=oai_www.internetculturale.sbn.it"
    assert ":" not in Path(elaboration.manifest_path).name
    assert "?" not in Path(elaboration.manifest_path).name
