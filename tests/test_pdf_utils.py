# test_pdf_utils.py – Creato il 2025-09-13
import os
import pytest
from pypdf import PdfReader
from pdf_utils import (
    create_pdf_from_images,
    enrich_pdf_metadata,
    _pdf_open_max_workers,
)

# -----------------------
# FIXTURE
# -----------------------

@pytest.fixture
def sample_images(tmp_path):
    """Crea due immagini RGB di test e restituisce i percorsi."""
    from PIL import Image
    paths = []
    for i in range(2):
        img = Image.new("RGB", (100, 100), color=(i * 100, i * 50, i * 25))
        path = tmp_path / f"img_{i}.png"
        img.save(path)
        paths.append(str(path))
    return paths

# -----------------------
# TEST create_pdf_from_images
# -----------------------

def test_create_pdf_from_valid_images(sample_images, tmp_path):
    output_pdf = tmp_path / "output.pdf"
    result = create_pdf_from_images(sample_images, str(output_pdf))
    assert result == str(output_pdf)
    assert os.path.exists(output_pdf)

@pytest.mark.parametrize("mode", ["RGB", "L", "RGBA", "P", "1"])
def test_image_modes_supported(mode, tmp_path):
    from PIL import Image
    img = Image.new(mode, (100, 100))
    path = tmp_path / f"img_{mode}.png"
    img.save(path)
    result = create_pdf_from_images([str(path)], str(tmp_path / "out.pdf"))
    assert result is not None
    assert os.path.exists(tmp_path / "out.pdf")

def test_create_pdf_from_empty_list(tmp_path):
    output_pdf = tmp_path / "empty.pdf"
    result = create_pdf_from_images([], str(output_pdf))
    assert result is None
    assert not os.path.exists(output_pdf)

def test_create_pdf_with_corrupted_image(monkeypatch, tmp_path):
    def fake_open(path):
        raise IOError("Corrupted image")
    monkeypatch.setattr("pdf_utils.Image.open", fake_open)
    result = create_pdf_from_images(["fake.png"], str(tmp_path / "out.pdf"))
    assert result is None


def test_pdf_open_max_workers_is_capped_for_memory():
    assert _pdf_open_max_workers(1, cpu_count=16) == 1
    assert _pdf_open_max_workers(2, cpu_count=16) == 2
    assert _pdf_open_max_workers(20, cpu_count=16) == 4
    assert _pdf_open_max_workers(20, cpu_count=2) == 2

# -----------------------
# TEST enrich_pdf_metadata
# -----------------------

def test_enrich_pdf_metadata_success(sample_images, tmp_path):
    pdf_path = tmp_path / "base.pdf"
    create_pdf_from_images(sample_images, str(pdf_path))
    success = enrich_pdf_metadata(str(pdf_path), "Titolo", "Soggetto", "UA_123", "ARK456")
    assert success is True
    reader = PdfReader(str(pdf_path))
    metadata = reader.metadata
    assert metadata["/Title"] == "Titolo"
    assert metadata["/Subject"] == "Soggetto"
    assert "UA_123" in metadata["/Keywords"]

def test_enrich_pdf_metadata_missing_file():
    result = enrich_pdf_metadata("non_esiste.pdf", "Titolo", "Soggetto", "UA", "ARK")
    assert result is False

@pytest.mark.parametrize("title,subject,ua,ark", [
    ("", "", "", ""),
    (None, None, None, None),
    ("Titolo", None, "UA", None),
])
def test_enrich_pdf_metadata_edge(title, subject, ua, ark, sample_images, tmp_path):
    pdf_path = tmp_path / "base.pdf"
    create_pdf_from_images(sample_images, str(pdf_path))
    assert enrich_pdf_metadata(str(pdf_path), title, subject, ua, ark) is True
