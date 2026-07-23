import json
from pathlib import Path


def test_ai_error_utils_classifies_common_runtime_cases():
    from src.ai_error_utils import classify_ai_runtime_error

    invalid_key = classify_ai_runtime_error("OpenAI", "unauthorized: invalid api key")
    quota = classify_ai_runtime_error("Gemini", "429 Resource exhausted")
    model = classify_ai_runtime_error("Claude", "404 model not found")
    response = classify_ai_runtime_error("OpenAI", "Risposta non valida: content missing")

    assert "Credenziali non valide" in invalid_key
    assert "Quota o limite richieste esaurito" in quota
    assert "Modello AI non disponibile" in model
    assert "risposta non valida o vuota" in response


def test_ai_search_dialog_excludes_transkribus_from_provider_combo(qtbot):
    import src.RicercaAssistitaAI as rai
    from src.key_manager import get_service_provider_labels

    dlg = rai.RicercaAssistitaAIDialog(None, glossario={}, lingua="it")
    qtbot.addWidget(dlg)

    providers = [dlg.combo_provider.itemText(i) for i in range(dlg.combo_provider.count())]
    assert "Transkribus" not in providers
    assert providers == list(get_service_provider_labels("ai_search"))


def test_ai_search_lazy_key_manager_wrappers_use_runtime_module(monkeypatch):
    import types
    import src.RicercaAssistitaAI as rai

    fake_module = types.SimpleNamespace(
        get_service_provider_labels=lambda service: ["Gemini", "Claude"] if service == "ai_search" else [],
        normalize_provider_name=lambda provider: f"norm::{provider}",
    )

    monkeypatch.setattr(rai, "_get_key_manager_module", lambda: fake_module)

    assert list(rai.get_service_provider_labels("ai_search")) == ["Gemini", "Claude"]
    assert rai.normalize_provider_name("Gemini") == "norm::Gemini"


def test_ai_search_dialog_uses_runtime_default_model_hint(qtbot):
    import src.RicercaAssistitaAI as rai

    dlg = rai.RicercaAssistitaAIDialog(None, glossario={}, lingua="it")
    qtbot.addWidget(dlg)

    dlg.combo_provider.setCurrentText("Claude")
    assert "claude-opus-4-5" in dlg.inp_custom_model.placeholderText()

    dlg.combo_provider.setCurrentText("Gemini")
    assert dlg.inp_custom_model.placeholderText() == "Modello custom (opzionale)"


def test_ai_worker_rejects_provider_outside_ai_search_service(monkeypatch):
    import src.RicercaAssistitaAI as rai

    worker = rai.RicercaAssistitaAIWorker("davini", "Transkribus", show_all=False)
    captured = {}
    worker.error.connect(lambda value: captured.setdefault("error", value))

    worker.run()

    assert "Provider non supportato per Ricerca Assistita AI" in captured["error"]


def test_ai_worker_show_all_keeps_json_available_after_provider_error(monkeypatch):
    import src.RicercaAssistitaAI as rai

    class FakeKeyManager:
        current_indices = {"Gemini": 0}

        def get_all_keys(self, provider):
            return ["fake-key"] if provider == "Gemini" else []

        def get_next_key(self, provider, current_key):
            return None

    class FailingHandler:
        def extract_genealogy(self, *args, **kwargs):
            raise RuntimeError("provider failure")

    monkeypatch.setattr(rai, "KeyManager", lambda: FakeKeyManager())
    monkeypatch.setattr(rai, "get_handler", lambda provider, key: FailingHandler())

    worker = rai.RicercaAssistitaAIWorker("davini", "Gemini", show_all=True)
    captured = {}
    worker.finished.connect(lambda value: captured.setdefault("value", value))
    worker.error.connect(lambda value: captured.setdefault("error", value))

    worker.run()

    assert "error" not in captured
    payload = json.loads(captured["value"])
    assert payload[0]["provider"] == "Gemini"
    assert "provider failure" in payload[0]["raw"]


def test_ai_worker_formats_last_provider_error_for_user(monkeypatch):
    import src.RicercaAssistitaAI as rai

    class FakeKeyManager:
        current_indices = {"Gemini": 0}

        def get_all_keys(self, provider):
            return ["fake-key"] if provider == "Gemini" else []

        def get_next_key(self, provider, current_key):
            return None

    class FailingHandler:
        def extract_genealogy(self, *args, **kwargs):
            raise RuntimeError("429 quota exceeded")

    monkeypatch.setattr(rai, "KeyManager", lambda: FakeKeyManager())
    monkeypatch.setattr(rai, "get_handler", lambda provider, key: FailingHandler())

    worker = rai.RicercaAssistitaAIWorker("davini", "Gemini", show_all=False)
    captured = {}
    worker.error.connect(lambda value: captured.setdefault("error", value))

    worker.run()

    assert "Quota o limite richieste esaurito" in captured["error"]


def test_ocr_preview_worker_formats_provider_error_for_user(monkeypatch):
    import src.ocr_dialog as ocr_dialog

    class FakeWorker:
        api_keys = ["fake-key"]

        def __init__(self, provider, api_key, formats, output_dir):
            self.provider = provider
            self.api_key = api_key
            self.current_key_idx = 0

        def _current_key(self):
            return self.api_keys[self.current_key_idx]

        def _rotate_key(self):
            return False

        def transcribe_top_preview(self, file_path, api_key, base_prompt):
            raise RuntimeError("429 quota exceeded")

    monkeypatch.setattr(ocr_dialog, "AdvancedOCRWorker", FakeWorker)

    worker = ocr_dialog.CalibrationThread("registro.jpg", "Gemini", "fake-key", "prompt")
    captured = {}
    worker.error.connect(lambda value: captured.setdefault("error", value))

    worker.run()

    assert "Quota o limite richieste esaurito" in captured["error"]


def test_ai_search_result_log_summary_avoids_payload_dump():
    from src.RicercaAssistitaAI import _summarize_ai_result_payload

    payload = json.dumps([
        {"provider": "Gemini", "results": [{"nome": "A"}, {"nome": "B"}]},
        {"provider": "OpenAI", "results": []},
    ])

    assert _summarize_ai_result_payload(payload) == "2 righe da 2 provider (Gemini, OpenAI)"


def test_gemini_split_merge_deduplicates_overlap_and_fills_blank_columns():
    from src.ocr_processor import AdvancedOCRWorker

    worker = object.__new__(AdvancedOCRWorker)
    top = "\n".join(
        [
            "N°Casa | N°Famiglia | N° | Cognome | Nome | Stato | Nota finale",
            "1 | 1 | 1 | Rossi | Anna | nubile | letto",
            "1 | 1 | 2 | Rossi | Bruno | celibe | letto",
            "2 | 1 | 3 | Bianchi | Carla | maritata | nota-top",
        ]
    )
    bottom = "\n".join(
        [
            "2 | 1 | 3 | Bianchi | Carla | maritata | ",
            "2 | 1 | 4 | Bianchi | Dario | celibe | nota-bottom",
        ]
    )

    merged = worker._merge_gemini_split_text(top, bottom)

    assert merged.count("Bianchi | Carla") == 1
    assert "2 | 1 | 3 | Bianchi | Carla | maritata | nota-top" in merged
    assert "2 | 1 | 4 | Bianchi | Dario | celibe | nota-bottom" in merged


def test_ocr_worker_uses_default_ollama_host_when_api_key_missing():
    from src.ocr_processor import AdvancedOCRWorker

    worker = AdvancedOCRWorker(
        provider="Ollama",
        api_key="",
        formats=["txt"],
        output_dir=".",
    )

    assert worker.api_keys == ["http://localhost:11434"]


def test_ocr_process_file_formats_last_provider_error_for_user(monkeypatch, tmp_path):
    from src.ocr_processor import AdvancedOCRWorker

    worker = AdvancedOCRWorker(
        provider="Gemini",
        api_key="fake-key",
        formats=["txt"],
        output_dir=str(tmp_path),
    )

    monkeypatch.setattr(worker, "_transcribe_image", lambda f_path, key: (_ for _ in ()).throw(RuntimeError("429 quota exceeded")))

    try:
        worker.process_file(str(tmp_path / "registro.jpg"))
    except Exception as exc:
        message = str(exc)
    else:
        raise AssertionError("Expected OCR process_file to fail")

    assert "Quota o limite richieste esaurito" in message


def test_gemini_split_merge_deduplicates_fuzzy_rows_without_progressive():
    from src.ocr_processor import AdvancedOCRWorker

    worker = object.__new__(AdvancedOCRWorker)
    top = "\n".join(
        [
            "N°Casa | N°Famiglia | N° | Cognome | Nome",
            "1 | 1 |  | Rossi | Anna",
            "1 | 1 |  | Rossi | Bruno",
        ]
    )
    bottom = "\n".join(
        [
            "1 | 1 |  | Rossi | Bruno",
            "1 | 1 |  | Verdi | Carla",
        ]
    )

    merged = worker._merge_gemini_split_text(top, bottom)

    assert merged.count("Rossi | Bruno") == 1
    assert "Verdi | Carla" in merged


def test_ocr_logs_do_not_include_key_prefixes():
    source = Path("src/ocr_processor.py").read_text(encoding="utf-8")

    assert "key[:6]" not in source
    assert "_current_key()[:6]" not in source


def test_ocr_split_diagnostics_are_saved_in_dedicated_subfolder(tmp_path):
    from src.ocr_processor import AdvancedOCRWorker

    worker = object.__new__(AdvancedOCRWorker)
    worker.output_dir = str(tmp_path)

    diag_dir = worker._save_split_diagnostics(
        str(tmp_path / "registro.jpg"),
        "top text",
        "bottom text",
    )

    assert Path(diag_dir) == tmp_path / "_ocr_diagnostics"
    assert (tmp_path / "_ocr_diagnostics" / "DIAG_registro_TOP.txt").read_text(encoding="utf-8") == "top text"
    assert (tmp_path / "_ocr_diagnostics" / "DIAG_registro_BOTTOM.txt").read_text(encoding="utf-8") == "bottom text"


def test_ocr_split_diagnostics_are_optional(tmp_path, monkeypatch):
    from src.ocr_processor import AdvancedOCRWorker

    worker = object.__new__(AdvancedOCRWorker)
    worker.custom_model = None
    worker.save_diagnostics = False

    monkeypatch.setattr(worker, "_transcribe_gemini", lambda api_key, b64_img, prompt, model=None: "riga 1")
    monkeypatch.setattr(worker, "_merge_gemini_split_text", lambda top, bottom: f"{top}\n{bottom}")

    class FakeImage:
        size = (2000, 1000)
        mode = "RGB"

        def crop(self, box):
            return self

        def resize(self, size, resample):
            return self

        def convert(self, mode):
            return self

        def save(self, fp, format=None, quality=None):
            fp.write(b"fake-image")

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

    monkeypatch.setattr("src.ocr_processor.Image.open", lambda path: FakeImage())

    result = worker._transcribe_gemini_split(str(tmp_path / "registro.jpg"), "fake-key", "prompt")

    assert result == "riga 1\nriga 1"
    assert not (tmp_path / "_ocr_diagnostics").exists()


def test_ai_search_logs_do_not_dump_query_or_result_payload():
    source = Path("src/RicercaAssistitaAI.py").read_text(encoding="utf-8")

    assert "query={self.query}" not in source
    assert "Ricerca completata: {r}" not in source
    assert "query='" not in source


def test_provider_runtime_defaults_are_not_duplicated_in_runtime_modules():
    translation_source = Path("src/translation_processor.py").read_text(encoding="utf-8")
    ocr_source = Path("src/ocr_processor.py").read_text(encoding="utf-8")
    ai_source = Path("src/multi_provider_handlers.py").read_text(encoding="utf-8")

    duplicated_literals = [
        "https://api.mistral.ai/v1",
        "https://api.groq.com/openai/v1",
        "https://api.deepseek.com",
        "https://api.x.ai/v1",
        "https://api-inference.huggingface.co/v1/",
        "mistral-large-latest",
        "pixtral-large-latest",
        "llama-3.3-70b-versatile",
        "llama-3.2-90b-vision-preview",
        "deepseek-chat",
        "grok-3-mini",
        "grok-2-vision-1212",
        "Qwen/Qwen2.5-72B-Instruct",
        "Qwen/Qwen2.5-VL-7B-Instruct",
        "claude-opus-4-5",
    ]

    for literal in duplicated_literals:
        assert literal not in translation_source
        assert literal not in ocr_source


def test_ocr_pdf_keeps_partial_progress_when_later_page_fails(monkeypatch, tmp_path):
    from src.ocr_processor import AdvancedOCRWorker

    worker = AdvancedOCRWorker(
        provider="Ollama",
        api_key="",
        formats=["txt"],
        output_dir=str(tmp_path),
    )

    class FakePix:
        def save(self, path):
            Path(path).write_bytes(b"fake-jpg")

    class FakePage:
        def get_pixmap(self, matrix=None, colorspace=None):
            return FakePix()

    class FakeDoc:
        def __len__(self):
            return 2

        def __getitem__(self, index):
            return FakePage()

        def close(self):
            return None

    class FakeFitz:
        csRGB = object()

        @staticmethod
        def open(path):
            return FakeDoc()

        @staticmethod
        def Matrix(x, y):
            return (x, y)

    calls = {"count": 0}

    def fake_transcribe(path, key):
        calls["count"] += 1
        if calls["count"] == 1:
            return "prima pagina"
        raise RuntimeError("429 quota exceeded")

    monkeypatch.setitem(__import__("sys").modules, "fitz", FakeFitz)
    monkeypatch.setattr(worker, "_transcribe_image", fake_transcribe)

    try:
        worker.process_file(str(tmp_path / "registro.pdf"))
    except Exception as exc:
        message = str(exc)
    else:
        raise AssertionError("Expected OCR PDF processing to fail")

    partial_path = tmp_path / "_ocr_progress" / "registro_trascrizione_parziale.txt"
    assert partial_path.exists()
    assert "--- Pagina 1 ---" in partial_path.read_text(encoding="utf-8")
    assert "prima pagina" in partial_path.read_text(encoding="utf-8")
    assert "Quota o limite richieste esaurito" in message


def test_ocr_pdf_closes_document_when_later_page_fails(monkeypatch, tmp_path):
    from src.ocr_processor import AdvancedOCRWorker

    worker = AdvancedOCRWorker(
        provider="Ollama",
        api_key="",
        formats=["txt"],
        output_dir=str(tmp_path),
    )

    class FakePix:
        def save(self, path):
            Path(path).write_bytes(b"fake-jpg")

    class FakePage:
        def get_pixmap(self, matrix=None, colorspace=None):
            return FakePix()

    closed = {"value": False}

    class FakeDoc:
        def __len__(self):
            return 2

        def __getitem__(self, index):
            return FakePage()

        def close(self):
            closed["value"] = True

    class FakeFitz:
        csRGB = object()

        @staticmethod
        def open(path):
            return FakeDoc()

        @staticmethod
        def Matrix(x, y):
            return (x, y)

    calls = {"count": 0}

    def fake_transcribe(path, key):
        calls["count"] += 1
        if calls["count"] == 1:
            return "prima pagina"
        raise RuntimeError("429 quota exceeded")

    monkeypatch.setitem(__import__("sys").modules, "fitz", FakeFitz)
    monkeypatch.setattr(worker, "_transcribe_image", fake_transcribe)

    try:
        worker.process_file(str(tmp_path / "registro.pdf"))
    except Exception:
        pass
    else:
        raise AssertionError("Expected OCR PDF processing to fail")

    assert closed["value"] is True


def test_ocr_pdf_clears_partial_progress_after_success(monkeypatch, tmp_path):
    from src.ocr_processor import AdvancedOCRWorker

    worker = AdvancedOCRWorker(
        provider="Ollama",
        api_key="",
        formats=["txt"],
        output_dir=str(tmp_path),
    )

    class FakePix:
        def save(self, path):
            Path(path).write_bytes(b"fake-jpg")

    class FakePage:
        def get_pixmap(self, matrix=None, colorspace=None):
            return FakePix()

    class FakeDoc:
        def __len__(self):
            return 2

        def __getitem__(self, index):
            return FakePage()

        def close(self):
            return None

    class FakeFitz:
        csRGB = object()

        @staticmethod
        def open(path):
            return FakeDoc()

        @staticmethod
        def Matrix(x, y):
            return (x, y)

    monkeypatch.setitem(__import__("sys").modules, "fitz", FakeFitz)
    monkeypatch.setattr(worker, "_transcribe_image", lambda path, key: f"testo:{Path(path).name}")

    worker.process_file(str(tmp_path / "registro.pdf"))

    partial_path = tmp_path / "_ocr_progress" / "registro_trascrizione_parziale.txt"
    final_txt = tmp_path / "registro_trascrizione.txt"

    assert not partial_path.exists()
    assert final_txt.exists()
    content = final_txt.read_text(encoding="utf-8")
    assert "--- Pagina 1 ---" in content
    assert "--- Pagina 2 ---" in content
