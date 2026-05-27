import pytest
import src.canvas_processor as cp

# --- is_canvas_valid ---
def test_is_canvas_valid_true():
    canvas = {"images": [{"resource": {"width": 400, "height": 400}}]}
    assert cp.is_canvas_valid(canvas) is True

def test_is_canvas_valid_false_dimensions():
    canvas = {"images": [{"resource": {"width": 200, "height": 400}}]}
    assert cp.is_canvas_valid(canvas) is False

def test_is_canvas_valid_invalid_structure():
    assert cp.is_canvas_valid({}) is False

# --- find_canvas_by_id ---
def test_find_canvas_by_id_found():
    manifest = {"sequences": [{"canvases": [{"@id": "abc/target"}]}]}
    assert cp.find_canvas_by_id(manifest, "target") == {"@id": "abc/target"}

def test_find_canvas_by_id_not_found():
    manifest = {"sequences": [{"canvases": [{"@id": "abc/other"}]}]}
    assert cp.find_canvas_by_id(manifest, "target") is None

def test_find_canvas_by_id_malformed():
    assert cp.find_canvas_by_id({}, "target") is None

# --- process_single_canvas ---
def test_process_single_canvas_no_canvas(monkeypatch):
    monkeypatch.setattr(cp, "find_canvas_by_id", lambda *a, **k: None)
    assert cp.process_single_canvas({}, "out", "id", ["PNG"]) is None

def test_process_single_canvas_invalid_canvas(monkeypatch):
    monkeypatch.setattr(cp, "find_canvas_by_id", lambda *a, **k: {"images": [{"resource": {"width": 100, "height": 100}}]})
    monkeypatch.setattr(cp, "is_canvas_valid", lambda *a, **k: False)
    assert cp.process_single_canvas({}, "out", "id", ["PNG"]) is None

def test_process_single_canvas_happy(monkeypatch, tmp_path):
    canvas = {
        "images": [{"resource": {"width": 400, "height": 400, "service": {"@id": "svc"}}}],
        "@id": "cid"
    }
    manifest = {}
    monkeypatch.setattr(cp, "find_canvas_by_id", lambda *a, **k: canvas)
    monkeypatch.setattr(cp, "is_canvas_valid", lambda *a, **k: True)
    monkeypatch.setattr(cp, "download_tiles", lambda info, td, **kwargs: None)
    monkeypatch.setattr(cp, "rebuild_image", lambda info, td, **kwargs: b"img")
    monkeypatch.setattr(cp, "save_image_variants", lambda *a, **k: None)
    monkeypatch.setattr(cp, "build_image_metadata", lambda **k: {"meta": "ok"})
    monkeypatch.setattr(cp, "estrai_metadati_da_manifest", lambda *a, **k: None)
    assert cp.process_single_canvas(manifest, tmp_path, "id", ["PNG"], manifest_path="mpath", page_url="url") is True

def test_process_single_canvas_exception(monkeypatch):
    canvas = {"images": [{"resource": {"width": 400, "height": 400, "service": {"@id": "svc"}}}]}
    monkeypatch.setattr(cp, "find_canvas_by_id", lambda *a, **k: canvas)
    monkeypatch.setattr(cp, "is_canvas_valid", lambda *a, **k: True)
    monkeypatch.setattr(cp, "download_tiles", lambda *a, **k: (_ for _ in ()).throw(RuntimeError("boom")))
    assert cp.process_single_canvas({}, "out", "id", ["PNG"]) is None

# --- process_all_canvases ---
def test_process_all_canvases_malformed_manifest():
    assert cp.process_all_canvases({}, "out", ["PNG"]) is None

def test_process_all_canvases_skip_invalid(monkeypatch):
    manifest = {"sequences": [{"canvases": [{"images": []}]}]}
    monkeypatch.setattr(cp, "is_canvas_valid", lambda *a, **k: False)
    assert cp.process_all_canvases(manifest, "out", ["PNG"]) is None

def test_process_all_canvases_happy_with_pdf_real(monkeypatch, tmp_path):
    prefix = "testprefix"
    canvas = {
        "images": [{"resource": {"width": 400, "height": 400, "service": {"@id": "svc"}}}],
        "label": "lbl",
        "@id": "cid-1"
    }
    manifest = {"sequences": [{"canvases": [canvas]}]}
    monkeypatch.setattr(cp, "is_canvas_valid", lambda *a, **k: True)
    monkeypatch.setattr(cp, "download_tiles", lambda info, td, **kwargs: None)
    monkeypatch.setattr(cp, "rebuild_image", lambda info, td, **kwargs: b"imgbytes")

    def fake_save_image_variants(image_bytes, out_dir, base_name="canvas", formats=("JPEG",), **kwargs):
        img_path = tmp_path / f"{prefix}_canvas_1.jpg"
        img_path.write_bytes(image_bytes)
        return [str(img_path)]

    monkeypatch.setattr(cp, "save_image_variants", fake_save_image_variants)
    monkeypatch.setattr(cp, "build_image_metadata", lambda **k: {"meta": "ok"})
    monkeypatch.setattr(cp, "enrich_pdf_metadata", lambda **k: None)
    monkeypatch.setattr(cp, "estrai_metadati_da_manifest", lambda *a, **k: None)

    def fake_create_pdf_from_images(images, output_pdf_path=None, **kwargs):
        Path(output_pdf_path).write_bytes(b"%PDF-1.4\n%...")
        return str(output_pdf_path)

    monkeypatch.setattr(cp, "create_pdf_from_images", fake_create_pdf_from_images)

    cp.process_all_canvases(manifest, tmp_path, ["JPEG"], base_filename_prefix=prefix, generate_pdf=True)
    pdf_file = tmp_path / f"{prefix}_registro_completo.pdf"
    assert pdf_file.exists()
    assert pdf_file.read_bytes().startswith(b"%PDF")

def test_process_all_canvases_pdf_no_images(monkeypatch, tmp_path):
    canvas = {
        "images": [{"resource": {"width": 400, "height": 400, "service": {"@id": "svc"}}}],
        "@id": "cid-1"
    }
    manifest = {"sequences": [{"canvases": [canvas]}]}
    monkeypatch.setattr(cp, "is_canvas_valid", lambda *a, **k: True)
    monkeypatch.setattr(cp, "download_tiles", lambda info, td, **kwargs: None)
    monkeypatch.setattr(cp, "rebuild_image", lambda info, td, **kwargs: b"imgbytes")
    monkeypatch.setattr(cp, "save_image_variants", lambda *a, **k: [])

    called = {"count": 0}
    def guard_create_pdf_from_images(*a, **k):
        called["count"] += 1
        return None

    monkeypatch.setattr(cp, "create_pdf_from_images", guard_create_pdf_from_images)
    cp.process_all_canvases(manifest, tmp_path, ["JPEG"], generate_pdf=True)
    assert called["count"] == 0

def test_process_all_canvases_exception_in_loop(monkeypatch):
    canvas = {"images": [{"resource": {"width": 400, "height": 400, "service": {"@id": "svc"}}}]}
    manifest = {"sequences": [{"canvases": [canvas]}]}
    monkeypatch.setattr(cp, "is_canvas_valid", lambda *a, **k: True)
    monkeypatch.setattr(cp, "download_tiles", lambda *a, **k: (_ for _ in ()).throw(RuntimeError("boom")))
    assert cp.process_all_canvases(manifest, "out", ["PNG"]) is None
