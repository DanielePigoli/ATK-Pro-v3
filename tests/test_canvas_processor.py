import os
import pytest
from pathlib import Path
import canvas_processor as cp



# -------------------------------
# Test su is_canvas_valid
# -------------------------------

def test_is_canvas_valid_false():
    # Canvas troppo piccolo
    canvas = {"images": [{"resource": {"width": 100, "height": 100}}]}
    assert not cp.is_canvas_valid(canvas)

def test_is_canvas_valid_true_with_resource():
    # Canvas valido: width/height >= 300 dentro resource
    canvas = {"images": [{"resource": {"width": 500, "height": 600}}]}
    assert cp.is_canvas_valid(canvas)


# -------------------------------
# Test su process_single_canvas
# -------------------------------

def test_process_single_canvas_success(monkeypatch, tmp_path):
    fake_manifest = {
        "sequences": [{
            "canvases": [{
                "@id": "c1",
                "images": [{
                    "resource": {
                        "width": 500,
                        "height": 500,
                        "service": {"@id": "http://s"}
                    }
                }]
            }]
        }]
    }


# 🔧 Canvas con service come lista
@pytest.fixture
def manifest_con_service_lista():
    return {
        "sequences": [{
            "canvases": [{
                "@id": "https://example.org/canvas/5",
                "label": "pagina 5",
                "images": [{
                    "resource": {
                        "width": 1000,
                        "height": 1500,
                        "service": [{"@id": "https://example.org/service/5"}]
                    }
                }]
            }]
        }]
    }


@pytest.fixture
def manifest_con_canvas_valido():
    # Manifest minimale con canvas identificabile che termina con '1'
    return {
        "sequences": [{
            "canvases": [{
                "@id": "https://example.org/canvas/1",
                "label": "pagina 1",
                "images": [{
                    "resource": {
                        "width": 1000,
                        "height": 1500,
                        "service": {"@id": "https://example.org/service/1"}
                    }
                }]
            }]
        }]
    }


def test_process_single_canvas_crea_file(tmp_path, manifest_con_canvas_valido, monkeypatch):
    monkeypatch.setattr(cp, "download_tiles", lambda info, path, **kwargs: None)
    monkeypatch.setattr(cp, "rebuild_image", lambda info, path, **kwargs: b"img")
    # Evitiamo la chiamata reale a requests.get per info.json
    monkeypatch.setattr(cp, "_get_info_json_for_canvas", lambda canvas: {"@id": "https://example.org/service/1"})
    monkeypatch.setattr(cp, "save_image_variants", lambda img, folder, name, formats, meta=None: Path(folder).joinpath(f"{name}.jpg").write_bytes(img))
    monkeypatch.setattr(cp, "build_image_metadata", lambda **kwargs: {})
    monkeypatch.setattr(cp, "estrai_metadati_da_manifest", lambda path, imgs: None)

    cp.process_single_canvas(
        manifest=manifest_con_canvas_valido,
        output_folder=str(tmp_path),
        target_canvas_id="1",
        formats=["JPG"],
        base_filename="canvas_test"
    )

    assert tmp_path.joinpath("canvas_test.jpg").exists()


def test_process_single_canvas_canvas_none(monkeypatch):
    monkeypatch.setattr(cp, "find_canvas_by_id", lambda *a, **k: None)
    result = cp.process_single_canvas({}, "out", "id", ["JPG"])
    assert result is None


def test_process_single_canvas_senza_service(monkeypatch):
    canvas = {"images": [{"resource": {"width": 1000, "height": 1500}}]}
    monkeypatch.setattr(cp, "find_canvas_by_id", lambda *a, **k: canvas)
    monkeypatch.setattr(cp, "is_canvas_valid", lambda *a, **k: True)
    result = cp.process_single_canvas({}, "out", "id", ["JPG"])
    assert result is None


def test_service_id_lista(monkeypatch, tmp_path, manifest_con_service_lista):
    monkeypatch.setattr(cp, "download_tiles", lambda info, path, **kwargs: None)
    monkeypatch.setattr(cp, "rebuild_image", lambda info, path, **kwargs: b"img")
    monkeypatch.setattr(cp, "save_image_variants", lambda img, folder, name, formats, meta=None: Path(folder).joinpath(f"{name}.jpg").write_bytes(img))
    monkeypatch.setattr(cp, "build_image_metadata", lambda **kwargs: {})
    monkeypatch.setattr(cp, "estrai_metadati_da_manifest", lambda path, imgs: None)

    result = cp.process_single_canvas(
        manifest=manifest_con_service_lista,
        output_folder=str(tmp_path),
        target_canvas_id="5",
        formats=["JPG"],
        base_filename="canvas_test"
    )

    assert tmp_path.joinpath("canvas_test.jpg").exists()
    assert result is True


def test_process_all_canvases_multipli(monkeypatch, tmp_path):
    manifest = {
        "sequences": [{
            "canvases": [
                {
                    "@id": "https://example.org/canvas/1",
                    "label": "pagina 1",
                    "images": [{
                        "resource": {
                            "width": 1000,
                            "height": 1500,
                            "service": {"@id": "https://example.org/service/1"}
                        }
                    }]
                },
                {
                    "@id": "https://example.org/canvas/2",
                    "label": "pagina 2",
                    "images": [{
                        "resource": {
                            "width": 1200,
                            "height": 1600,
                            "service": {"@id": "https://example.org/service/2"}
                        }
                    }]
                }
            ]
        }]
    }

    monkeypatch.setattr(cp, "download_tiles", lambda info, path, **kwargs: None)
    monkeypatch.setattr(cp, "rebuild_image", lambda info, path, **kwargs: b"img")
    monkeypatch.setattr(cp, "save_image_variants", lambda img, folder, name, formats, meta=None: Path(folder).joinpath(f"{name}.jpg").write_bytes(img))
    monkeypatch.setattr(cp, "build_image_metadata", lambda **kwargs: {})
    monkeypatch.setattr(cp, "estrai_metadati_da_manifest", lambda path, imgs: None)

    cp.process_all_canvases(
        manifest=manifest,
        output_folder=str(tmp_path),
        formats=["JPG"],
        base_filename_prefix="registro_test"
    )

    assert tmp_path.joinpath("registro_test_canvas_1.jpg").exists()
    assert tmp_path.joinpath("registro_test_canvas_2.jpg").exists()


def test_process_all_canvases_manifest_mancante():
    result = cp.process_all_canvases({}, "out", ["JPG"])
    assert result is None


def test_extract_service_id_lista():
    canvas = {"images": [{"resource": {"service": [{"@id": "svc-lista"}]}}]}
    sid = cp._extract_service_id(canvas)
    assert sid == "svc-lista"


def test_extract_service_id_mancante():
    canvas = {"images": [{"resource": {}}]}
    sid = cp._extract_service_id(canvas)
    assert sid is None


def test_extract_dimensions_fallback():
    canvas = {
        "images": [{"resource": {"width": 800, "height": 600}}],
        "width": None,
        "height": None
    }
    w, h = cp._extract_dimensions(canvas)
    assert w == 800 and h == 600
