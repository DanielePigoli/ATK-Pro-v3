from src import main_gui_qt as gui


class _FakePixmap:
    def __init__(self, path="", null=False):
        self.path = path
        self._null = null

    def isNull(self):
        return self._null


def test_load_cached_pixmap_with_fallback_returns_first_valid(monkeypatch):
    def fake_get_pixmap(path):
        if path == "first":
            return _FakePixmap(path, null=True)
        if path == "second":
            return _FakePixmap(path, null=False)
        return _FakePixmap(path, null=True)

    monkeypatch.setattr(gui, "get_pixmap_cached", fake_get_pixmap)

    pixmap, label = gui._load_cached_pixmap_with_fallback(
        ("first", "PNG"),
        ("second", "WEBP"),
    )

    assert pixmap.path == "second"
    assert label == "WEBP"


def test_load_cached_pixmap_with_fallback_returns_last_null_when_all_fail(monkeypatch):
    monkeypatch.setattr(gui, "get_pixmap_cached", lambda path: _FakePixmap(path, null=True))

    pixmap, label = gui._load_cached_pixmap_with_fallback(
        ("first", "PNG"),
        ("second", "WEBP"),
    )

    assert pixmap.path == "second"
    assert label is None
