import sys
import types

import src.translation_processor as translation_processor


def test_translation_processor_imports_logging():
    assert hasattr(translation_processor, "logging")


def test_translation_worker_emits_missing_credentials_for_remote_provider(monkeypatch):
    expected_message = "missing credentials for Gemini"
    fake_key_manager_module = types.SimpleNamespace(
        KeyManager=lambda: types.SimpleNamespace(get_all_keys=lambda provider: []),
        missing_provider_credentials_message=lambda provider: expected_message,
    )
    monkeypatch.setitem(sys.modules, "key_manager", fake_key_manager_module)
    monkeypatch.setattr(
        translation_processor,
        "missing_provider_credentials_message",
        fake_key_manager_module.missing_provider_credentials_message,
    )

    worker = translation_processor.TranslationWorker(
        provider="Gemini",
        api_key="",
        source_text="testo",
        target_lang_autonym="Italiano",
    )

    captured = {}
    worker.finished.connect(lambda success, message: captured.update({"success": success, "message": message}))

    worker.run()

    assert captured["success"] is False
    assert captured["message"] == expected_message


def test_translation_worker_uses_default_ollama_host_when_api_key_missing(monkeypatch):
    fake_key_manager_module = types.SimpleNamespace(
        KeyManager=lambda: types.SimpleNamespace(get_all_keys=lambda provider: []),
        missing_provider_credentials_message=lambda provider: f"missing credentials for {provider}",
    )
    monkeypatch.setitem(sys.modules, "key_manager", fake_key_manager_module)
    monkeypatch.setattr(
        translation_processor,
        "missing_provider_credentials_message",
        fake_key_manager_module.missing_provider_credentials_message,
    )

    worker = translation_processor.TranslationWorker(
        provider="Ollama",
        api_key="",
        source_text="testo",
        target_lang_autonym="Italiano",
    )

    assert worker.api_keys == ["http://localhost:11434"]


def test_translation_worker_rejects_provider_outside_translation_service():
    worker = translation_processor.TranslationWorker(
        provider="Transkribus",
        api_key="token",
        source_text="testo",
        target_lang_autonym="Italiano",
    )

    captured = {}
    worker.finished.connect(lambda success, message: captured.update({"success": success, "message": message}))

    worker.run()

    assert captured["success"] is False
    assert "Provider non supportato per Traduzione" in captured["message"]


def test_translation_worker_formats_quota_error_for_user(monkeypatch):
    worker = translation_processor.TranslationWorker(
        provider="Gemini",
        api_key="fake-key",
        source_text="testo",
        target_lang_autonym="Italiano",
    )

    monkeypatch.setattr(
        worker,
        "_call_gemini_model",
        lambda model, prompt: (_ for _ in ()).throw(RuntimeError("429 quota exceeded")),
    )

    class FakeModel:
        pass

    fake_genai = types.SimpleNamespace(
        configure=lambda api_key: None,
        GenerativeModel=lambda model_name: FakeModel(),
    )
    monkeypatch.setattr(translation_processor, "genai", fake_genai)

    fake_ai_utils = types.SimpleNamespace(get_best_gemini_model=lambda key, preferred="flash": "gemini-test")
    monkeypatch.setitem(sys.modules, "ai_utils", fake_ai_utils)

    captured = {}
    worker.finished.connect(lambda success, message: captured.update({"success": success, "message": message}))

    worker.run()

    assert captured["success"] is False
    assert "Quota o limite richieste esaurito" in captured["message"]


def test_translation_worker_formats_model_error_for_user(monkeypatch):
    worker = translation_processor.TranslationWorker(
        provider="OpenAI",
        api_key="fake-key",
        source_text="testo",
        target_lang_autonym="Italiano",
    )

    monkeypatch.setattr(
        worker,
        "_call_openai",
        lambda prompt, model=None: (_ for _ in ()).throw(RuntimeError("404 model not found")),
    )
    monkeypatch.setattr(translation_processor.openai, "OpenAI", lambda api_key: object())

    captured = {}
    worker.finished.connect(lambda success, message: captured.update({"success": success, "message": message}))

    worker.run()

    assert captured["success"] is False
    assert "Modello AI non disponibile" in captured["message"]
