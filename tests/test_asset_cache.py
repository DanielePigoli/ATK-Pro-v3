from src.asset_cache import AssetCache, MAX_TEXT_CACHE_BYTES, MAX_TEXT_CACHE_ITEMS


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
