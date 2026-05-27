import os
from PIL import Image
import image_rebuilder

class DummyImage:
    def __init__(self):
        self.pasted = []
    def paste(self, tile, box):
        self.pasted.append((tile, box))

def test_rebuild_image_from_tiles(monkeypatch, tmp_path):
    # Crea due tile fittizi con nomi coerenti con la griglia attesa
    tile1 = tmp_path / "tile_0_0.jpg"
    tile2 = tmp_path / "tile_1_0.jpg"
    tile1.write_bytes(b"fake")
    tile2.write_bytes(b"fake")

    # Info fittizie: 2 colonne × 1 riga
    info = {
        "width": 200,
        "height": 100,
        "tiles": [{"width": 100, "height": 100}],
    }

    dummy_img = DummyImage()

    def fake_open(path):
        return f"tile:{os.path.basename(path)}"

    def fake_new(mode, size, color=None):
        assert mode == "RGB"
        assert size == (200, 100)
        assert color == (255, 255, 255)
        return dummy_img

    monkeypatch.setattr(Image, "open", lambda path: fake_open(path))
    monkeypatch.setattr(Image, "new", fake_new)

    result = image_rebuilder.rebuild_image(info, str(tmp_path))

    assert result is dummy_img
    assert len(dummy_img.pasted) == 2
    assert any("tile_0_0.jpg" in t for t, _ in dummy_img.pasted)
    assert any("tile_1_0.jpg" in t for t, _ in dummy_img.pasted)
