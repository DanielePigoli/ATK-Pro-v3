import os
import pytest
from unittest.mock import MagicMock
import src.tile_downloader as td


def test_new_antenati_iiif_host_uses_antenati_headers():
    headers = td._headers_for_tile_url(
        "https://iiif-antenati.cultura.gov.it/iiif/2/wQNNjzL/0,0,256,256/full/0/default.jpg"
    )

    assert headers["Referer"] == "https://antenati.cultura.gov.it/"
    assert headers["Origin"] == "https://antenati.cultura.gov.it"


def test_download_tile_success(tmp_path, monkeypatch, caplog):
    class DummyResponse:
        status_code = 200
        def iter_content(self, chunk_size=8192):
            yield b"x" * 2048

    monkeypatch.setattr(td.requests, "get", lambda *a, **k: DummyResponse())

    out_file = tmp_path / "tile_0_0.jpg"
    with caplog.at_level("INFO"):
        td.download_tile("http://fake", 0, 0, 256, tmp_path)

    assert out_file.exists()
    assert out_file.stat().st_size > 1024
    assert any("Tile salvato correttamente" in rec.message for rec in caplog.records)


def test_download_tile_already_exists(tmp_path, monkeypatch, caplog):
    out_file = tmp_path / "tile_0_0.jpg"
    out_file.write_bytes(b"x" * 2048)

    called = {}
    def fake_get(*a, **k):
        called["yes"] = True
        return None

    monkeypatch.setattr(td.requests, "get", fake_get)

    with caplog.at_level("INFO"):
        td.download_tile("http://fake", 0, 0, 256, tmp_path)

    assert "yes" not in called
    assert any("Tile già presente e valido" in rec.message for rec in caplog.records)


def test_download_tile_http_error(tmp_path, monkeypatch, caplog):
    class DummyResponse:
        status_code = 500
        def iter_content(self, chunk_size=8192): return []

    monkeypatch.setattr(td.requests, "get", lambda *a, **k: DummyResponse())

    with caplog.at_level("ERROR"):
        td.download_tile("http://fake", 0, 0, 256, tmp_path)

    assert any("Errore HTTP" in rec.message for rec in caplog.records)


def test_download_tile_too_small(tmp_path, monkeypatch, caplog):
    class DummyResponse:
        status_code = 200
        def iter_content(self, chunk_size=8192):
            yield b"x" * 10

    monkeypatch.setattr(td.requests, "get", lambda *a, **k: DummyResponse())

    out_file = tmp_path / "tile_0_0.jpg"
    with caplog.at_level("WARNING"):
        td.download_tile("http://fake", 0, 0, 256, tmp_path)

    assert not out_file.exists()
    assert any("Tile troppo piccolo" in rec.message for rec in caplog.records)


def test_download_tile_retries_incomplete_chunked_stream(tmp_path, monkeypatch, caplog):
    calls = {"count": 0}

    class BrokenResponse:
        status_code = 200

        def iter_content(self, chunk_size=8192):
            yield b"x" * 1024
            raise td.requests.exceptions.ChunkedEncodingError("incomplete chunked read")

    class GoodResponse:
        status_code = 200

        def iter_content(self, chunk_size=8192):
            yield b"x" * 2048

    def fake_get(*a, **k):
        calls["count"] += 1
        return BrokenResponse() if calls["count"] == 1 else GoodResponse()

    monkeypatch.setattr(td.requests, "get", fake_get)
    monkeypatch.setattr(td.time, "sleep", lambda *a, **k: None)

    out_file = tmp_path / "tile_0_0.jpg"
    with caplog.at_level("WARNING"):
        result = td.download_tile("http://fake", 0, 0, 256, tmp_path)

    assert result == str(out_file)
    assert out_file.exists()
    assert out_file.stat().st_size == 2048
    assert not (tmp_path / "tile_0_0.jpg.part").exists()
    assert calls["count"] == 2
    assert any("interrotto durante lo stream" in rec.message for rec in caplog.records)


def test_download_tiles_invokes_download_tile(monkeypatch):
    info = {
        "@id": "http://fake",
        "width": 512,
        "height": 512,
        "tiles": [{"width": 256}],
    }

    called = []
    def fake_download_tile(base_url, x, y, tile_size, output_dir, *args):
        called.append((x, y))

    monkeypatch.setattr(td, "download_tile", fake_download_tile)

    td.download_tiles(info, "outdir")
    assert set(called) == {(0, 0), (1, 0), (0, 1), (1, 1)}


def test_download_tiles_uses_image_api_v3_size_keyword(tmp_path, monkeypatch):
    info = {
        "id": "https://example.org/iiif/image",
        "type": "ImageService3",
        "width": 256,
        "height": 256,
        "tiles": [{"width": 256}],
    }

    calls = []

    def fake_download_tile(base_url, x, y, tile_size, output_dir, quality, width, height, inter_delay, referer, size_keyword):
        calls.append((base_url, size_keyword))
        filename = os.path.join(output_dir, f"tile_{x}_{y}.jpg")
        with open(filename, "wb") as fh:
            fh.write(b"x" * 2048)
        return filename

    monkeypatch.setattr(td, "download_tile", fake_download_tile)

    td.download_tiles(info, tmp_path)

    assert calls == [("https://example.org/iiif/image", "max")]


def test_download_tiles_applies_registry_delay_for_heidelberg(tmp_path, monkeypatch):
    info = {
        "@id": "http://fake",
        "width": 256,
        "height": 256,
        "tiles": [{"width": 256}],
    }

    delays = []

    def fake_download_tile(base_url, x, y, tile_size, output_dir, quality, width, height, inter_delay):
        delays.append(inter_delay)
        filename = os.path.join(output_dir, f"tile_{x}_{y}.jpg")
        with open(filename, "wb") as fh:
            fh.write(b"x" * 2048)
        return filename

    monkeypatch.setattr(td, "download_tile", fake_download_tile)

    tiles_ok, tiles_missing = td.download_tiles(info, tmp_path, portale="heidelberg")

    assert delays == [0.3]
    assert len(tiles_ok) == 1
    assert tiles_missing == []


def test_download_tiles_uses_resource_profile_for_parallelism(tmp_path, monkeypatch):
    info = {
        "@id": "http://fake",
        "width": 512,
        "height": 512,
        "tiles": [{"width": 256}],
    }

    captured = {}

    class DummyExecutor:
        def __init__(self, max_workers):
            captured["max_workers"] = max_workers

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

        def submit(self, fn, *args, **kwargs):
            class DummyFuture:
                def result(self_inner):
                    return fn(*args, **kwargs)

            return DummyFuture()

    def fake_as_completed(futures):
        return list(futures)

    def fake_get_tile_download_max_workers(profile, *, portal_max_workers=None, cpu_count=None):
        captured["profile"] = profile
        captured["portal_max_workers"] = portal_max_workers
        return 3

    def fake_download_tile(base_url, x, y, tile_size, output_dir, *args):
        filename = os.path.join(output_dir, f"tile_{x}_{y}.jpg")
        with open(filename, "wb") as fh:
            fh.write(b"x" * 2048)
        return filename

    monkeypatch.setattr(td, "download_tile", fake_download_tile)
    monkeypatch.setattr(td, "get_tile_download_max_workers", fake_get_tile_download_max_workers)
    monkeypatch.setattr(td.concurrent.futures, "ThreadPoolExecutor", DummyExecutor)
    monkeypatch.setattr(td.concurrent.futures, "as_completed", fake_as_completed)

    tiles_ok, tiles_missing = td.download_tiles(info, tmp_path, resource_profile="leggero")

    assert captured["profile"] == "leggero"
    assert captured["portal_max_workers"] is None
    assert captured["max_workers"] == 3
    assert len(tiles_ok) == 4
    assert tiles_missing == []
