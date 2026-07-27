import sys
import os
import types

# === Mock immediato di tkinter e sottocomponenti ===
class _MockWidget:
    """Mock di un widget Tk con metodi comuni."""
    def pack(self, *a, **k): pass
    def grid(self, *a, **k): pass
    def place(self, *a, **k): pass
    def config(self, *a, **k): pass
    def destroy(self): pass

class _MockTk(_MockWidget):
    """Mock di un'istanza Tk con metodi minimi usati nel codice."""
    def withdraw(self): pass
    def mainloop(self): pass
    def title(self, *a, **k): pass

class _MockBooleanVar:
    def __init__(self, value=False):
        self._value = value
    def get(self): return self._value
    def set(self, value): self._value = value

# Modulo principale tkinter
mock_tk = types.ModuleType("tkinter")
mock_tk.Tk = lambda *a, **k: _MockTk()
mock_tk.TclError = Exception
mock_tk.END = "end"
mock_tk.WORD = "word"
mock_tk.Label = lambda *a, **k: _MockWidget()
mock_tk.Frame = lambda *a, **k: _MockWidget()
mock_tk.Button = lambda *a, **k: _MockWidget()
mock_tk.Entry = lambda *a, **k: _MockWidget()
mock_tk.Text = lambda *a, **k: _MockWidget()
mock_tk.Checkbutton = lambda *a, **k: _MockWidget()
mock_tk.BooleanVar = _MockBooleanVar

# Sottomodulo filedialog
mock_filedialog = types.ModuleType("tkinter.filedialog")
mock_filedialog.askopenfilename = lambda *a, **k: ""
mock_filedialog.askopenfilenames = lambda *a, **k: []
mock_filedialog.asksaveasfilename = lambda *a, **k: ""
mock_filedialog.askdirectory = lambda *a, **k: ""

# Sottomodulo messagebox
mock_messagebox = types.ModuleType("tkinter.messagebox")
mock_messagebox.showinfo = lambda *a, **k: None
mock_messagebox.showerror = lambda *a, **k: None
mock_messagebox.askyesno = lambda *a, **k: True

# Registra tutto in sys.modules
sys.modules["tkinter"] = mock_tk
sys.modules["tkinter.filedialog"] = mock_filedialog
sys.modules["tkinter.messagebox"] = mock_messagebox

# === Path setup ===
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))
root = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
if root not in sys.path:
    sys.path.insert(0, root)

# === Compatibilita opzionale con moduli storici esterni ===
from pathlib import Path
legacy_sezionale_path = os.environ.get("ATK_PRO_LEGACY_SEZIONALE_PATH")
if legacy_sezionale_path:
    legacy_path = Path(legacy_sezionale_path)
    if legacy_path.exists() and str(legacy_path) not in sys.path:
        sys.path.insert(0, str(legacy_path))

# === Fixture di supporto ===
import pytest
from PIL import Image

PLAYWRIGHT_TEST_FILES = {
    "test_browser_setup.py",
    "test_browser_setup_extra.py",
    "test_canvas_id_extractor_complete.py",
    "test_canvas_id_extractor_fallbacks.py",
    "test_canvas_id_extractor_gap_completion.py",
    "test_canvas_id_extractor_gap_forzati.py",
    "test_direct_manifest_resolution_order.py",
}

QT_RUNTIME_TEST_FILES = {
    "test_qt_progressdialog.py",
    "test_worker_shutdown.py",
}

INTEGRATION_TEST_FILES = {
    "test_bdl_direct_pdf.py",
    "test_bdt_direct_pdf.py",
    "test_bdt_direct_pdf_policy.py",
    "test_canvas_processor.py",
    "test_canvas_processor_extra.py",
    "test_canvas_processor_fallisce.py",
    "test_direct_manifest_resolution_order.py",
    "test_elaborazione_manifest_persistence.py",
    "test_esegui_elaborazione_headless.py",
    "test_ficlit_direct_image.py",
    "test_loader_and_rebuild.py",
    "test_main.py",
    "test_main_extra.py",
    "test_pdf_confirmation_mainthread.py",
    "test_pdf_formato_feature.py",
    "test_pdf_integration.py",
    "test_portal_adapters.py",
    "test_portal_live_smoke_matrix.py",
    "test_portal_registry.py",
    "test_qt_worker_coverage.py",
    "test_tile_downloader.py",
    "test_tile_downloader_resilience.py",
}

INTEGRATION_FILENAME_SNIPPETS = (
    "_technical_probe.py",
    "_direct_pdf.py",
    "_direct_image.py",
    "_live_smoke",
)


def _item_filename(item):
    item_path = getattr(item, "path", None)
    if item_path is not None:
        return Path(item_path).name
    return Path(str(item.fspath)).name


def _is_cli_test(item):
    item_path = getattr(item, "path", None)
    if item_path is not None:
        return "tests\\cli\\" in str(item_path) or "tests/cli/" in str(item_path)
    return "tests\\cli\\" in str(item.fspath) or "tests/cli/" in str(item.fspath)


def _is_integration_test(item, filename):
    if filename in INTEGRATION_TEST_FILES:
        return True
    if any(snippet in filename for snippet in INTEGRATION_FILENAME_SNIPPETS):
        return True
    if _is_cli_test(item):
        return True
    if "qtbot" in getattr(item, "fixturenames", ()):
        return True
    if filename in QT_RUNTIME_TEST_FILES or filename in PLAYWRIGHT_TEST_FILES:
        return True
    if item.nodeid.endswith(
        "test_pdf_formato_feature.py::TestProcessDocumentPDF::"
        "test_antenati_ud_prefers_html_canvas_before_playwright"
    ):
        return True
    return False


def pytest_collection_modifyitems(config, items):
    for item in items:
        filename = _item_filename(item)

        if "qtbot" in getattr(item, "fixturenames", ()):
            item.add_marker(pytest.mark.gui)
        elif filename in QT_RUNTIME_TEST_FILES:
            item.add_marker(pytest.mark.gui)

        if filename in PLAYWRIGHT_TEST_FILES:
            item.add_marker(pytest.mark.playwright)
        elif item.nodeid.endswith(
            "test_pdf_formato_feature.py::TestProcessDocumentPDF::"
            "test_antenati_ud_prefers_html_canvas_before_playwright"
        ):
            item.add_marker(pytest.mark.playwright)

        if _is_integration_test(item, filename):
            item.add_marker(pytest.mark.integration)
        else:
            item.add_marker(pytest.mark.unit)


@pytest.fixture
def sample_tiles(tmp_path):
    """Crea una cartella 'tiles' con una griglia 2×2 di PNG 10×10 px."""
    tiles_dir = tmp_path / "tiles"
    tiles_dir.mkdir()
    for row in range(2):
        for col in range(2):
            img = Image.new("RGB", (10, 10), color=(row * 80, col * 80, 150))
            path = tiles_dir / f"{row}_{col}.png"
            img.save(path)
    return tiles_dir
