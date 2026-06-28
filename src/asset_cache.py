import threading
from collections import OrderedDict
from PySide6.QtGui import QPixmap

MAX_TEXT_CACHE_ITEMS = 24
MAX_TEXT_CACHE_BYTES = 1 * 1024 * 1024

class AssetCache:
    def __init__(self):
        self._pixmap_cache = {}
        self._text_cache = OrderedDict()
        self._lock = threading.Lock()

    def get_pixmap(self, path):
        import time
        import logging
        start = time.perf_counter()
        with self._lock:
            if path in self._pixmap_cache:
                elapsed = (time.perf_counter() - start) * 1000
                logging.debug(f"[CACHE] get_pixmap HIT {path} ({elapsed:.2f} ms)")
                return self._pixmap_cache[path]
        pixmap = QPixmap(path)
        with self._lock:
            self._pixmap_cache[path] = pixmap
        elapsed = (time.perf_counter() - start) * 1000
        logging.debug(f"[CACHE] get_pixmap MISS {path} ({elapsed:.2f} ms)")
        return pixmap

    def get_text(self, path, encoding="utf-8"):
        import time
        import logging
        start = time.perf_counter()
        with self._lock:
            if path in self._text_cache:
                text = self._text_cache.pop(path)
                self._text_cache[path] = text
                elapsed = (time.perf_counter() - start) * 1000
                logging.debug(f"[CACHE] get_text HIT {path} ({elapsed:.2f} ms)")
                return text
        try:
            with open(path, "r", encoding=encoding) as f:
                text = f.read()
        except UnicodeDecodeError:
            with open(path, "r", encoding="latin-1") as f:
                text = f.read()
        if len(text.encode(encoding, errors="ignore")) <= MAX_TEXT_CACHE_BYTES:
            with self._lock:
                self._text_cache[path] = text
                while len(self._text_cache) > MAX_TEXT_CACHE_ITEMS:
                    self._text_cache.popitem(last=False)
        elapsed = (time.perf_counter() - start) * 1000
        logging.debug(f"[CACHE] get_text MISS {path} ({elapsed:.2f} ms)")
        return text

    def clear(self):
        with self._lock:
            self._pixmap_cache.clear()
            self._text_cache.clear()

# Istanza globale
asset_cache = AssetCache()

def get_pixmap_cached(path):
    return asset_cache.get_pixmap(path)

def get_text_cached(path, encoding="utf-8"):
    return asset_cache.get_text(path, encoding)
