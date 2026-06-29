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
