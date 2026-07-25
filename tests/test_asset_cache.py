from src.asset_cache import (
    AssetCache,
    MAX_PIXMAP_CACHE_ITEMS,
    MAX_TEXT_CACHE_BYTES,
    MAX_TEXT_CACHE_ITEMS,
)


def test_text_cache_skips_large_files(tmp_path):
    path = tmp_path / "large.txt"
    path.write_text("x" * (MAX_TEXT_CACHE_BYTES + 1), encoding="utf-8")

    cache = AssetCache()
    assert cache.get_text(str(path)) == "x" * (MAX_TEXT_CACHE_BYTES + 1)

    assert str(path) not in cache._text_cache


def test_text_cache_keeps_recent_small_files(tmp_path):
    cache = AssetCache()

    for idx in range(MAX_TEXT_CACHE_ITEMS + 1):
        path = tmp_path / f"{idx}.txt"
        path.write_text(str(idx), encoding="utf-8")
        assert cache.get_text(str(path)) == str(idx)

    assert len(cache._text_cache) == MAX_TEXT_CACHE_ITEMS
    assert str(tmp_path / "0.txt") not in cache._text_cache
    assert str(tmp_path / f"{MAX_TEXT_CACHE_ITEMS}.txt") in cache._text_cache


def test_pixmap_cache_keeps_recent_items(monkeypatch):
    created = []

    class FakePixmap:
        def __init__(self, path):
            self.path = path
            created.append(path)

    monkeypatch.setattr("src.asset_cache.QPixmap", FakePixmap)

    cache = AssetCache()
    for idx in range(MAX_PIXMAP_CACHE_ITEMS + 1):
        pixmap = cache.get_pixmap(f"img_{idx}.png")
        assert pixmap.path == f"img_{idx}.png"

    assert len(cache._pixmap_cache) == MAX_PIXMAP_CACHE_ITEMS
    assert "img_0.png" not in cache._pixmap_cache
    assert f"img_{MAX_PIXMAP_CACHE_ITEMS}.png" in cache._pixmap_cache


def test_pixmap_cache_hit_refreshes_lru(monkeypatch):
    class FakePixmap:
        def __init__(self, path):
            self.path = path

    monkeypatch.setattr("src.asset_cache.QPixmap", FakePixmap)

    cache = AssetCache()
    for idx in range(MAX_PIXMAP_CACHE_ITEMS):
        cache.get_pixmap(f"img_{idx}.png")

    cache.get_pixmap("img_0.png")
    cache.get_pixmap("img_new.png")

    assert "img_1.png" not in cache._pixmap_cache
    assert "img_0.png" in cache._pixmap_cache
