import json
import sys
import types

from PySide6.QtWidgets import QApplication


def test_translation_dialog_lazy_key_manager_wrappers_use_runtime_module(monkeypatch):
    import src.translation_dialog as translation_dialog

    fake_module = types.SimpleNamespace(
        missing_provider_credentials_message=lambda provider: f"missing::{provider}",
        provider_requires_credentials=lambda provider: provider != "Ollama",
    )

    monkeypatch.setattr(translation_dialog, "_get_key_manager_module", lambda: fake_module)

    assert translation_dialog.missing_provider_credentials_message("Gemini") == "missing::Gemini"
    assert translation_dialog.provider_requires_credentials("Gemini")


def test_translation_dialog_preloads_cassaforte_key(monkeypatch, tmp_path, qtbot):
    fake_key_manager_module = types.SimpleNamespace(
        KeyManager=lambda: types.SimpleNamespace(
            get_all_keys=lambda provider: ["vault-key-123"] if provider == "Gemini" else []
        ),
        get_provider_base_url=lambda provider: "",
        get_provider_default_host=lambda provider: "http://localhost:11434" if provider == "Ollama" else "",
        get_provider_default_model=lambda provider, service: {
            ("Ollama", "translation"): "llama3.2",
            ("HuggingFace", "translation"): "Qwen/Qwen2.5-72B-Instruct",
        }.get((provider, service), ""),
        require_provider_default_host=lambda provider: "http://localhost:11434" if provider == "Ollama" else "",
        require_provider_default_model=lambda provider, service: {
            ("Ollama", "translation"): "llama3.2",
            ("HuggingFace", "translation"): "Qwen/Qwen2.5-72B-Instruct",
        }.get((provider, service), ""),
        missing_provider_credentials_message=lambda provider: f"missing credentials for {provider}",
        normalize_provider_name=lambda provider: "Gemini" if "Gemini" in str(provider) else provider,
        provider_requires_credentials=lambda provider: provider != "Ollama",
        service_supports_provider=lambda service, provider: True,
        preload_vault_key=lambda provider, current_value="", key_manager=None: current_value or (
            "vault-key-123" if provider == "Gemini" else ""
        ),
    )
    monkeypatch.setitem(sys.modules, "key_manager", fake_key_manager_module)

    config_path = tmp_path / "config.json"
    config_path.write_text(
        json.dumps(
            {
                "ocr_provider": 2,
                "translation_context": "contesto",
                "translation_custom_model": "",
            }
        ),
        encoding="utf-8",
    )

    import src.translation_dialog as translation_dialog

    monkeypatch.setattr(
        translation_dialog,
        "get_msg",
        lambda glossario, chiave, lingua: chiave,
    )
    monkeypatch.setattr(
        translation_dialog,
        "TARGET_LANGUAGE_BY_INTERFACE",
        translation_dialog.TARGET_LANGUAGE_BY_INTERFACE.copy(),
    )
    monkeypatch.setattr(
        translation_dialog,
        "QApplication",
        QApplication,
        raising=False,
    )
    monkeypatch.setattr(
        "config_utils._config_file_path",
        lambda: str(config_path),
    )

    dlg = translation_dialog.TranslationDialog(None, glossario_data={}, lingua_corrente="it")
    qtbot.addWidget(dlg)

    assert dlg.txt_api.text() == "vault-key-123"


def test_translation_dialog_clears_remote_key_when_ollama_is_selected(monkeypatch, tmp_path, qtbot):
    fake_key_manager_module = types.SimpleNamespace(
        KeyManager=lambda: types.SimpleNamespace(
            get_all_keys=lambda provider: ["vault-key-123"] if provider == "Gemini" else []
        ),
        get_provider_base_url=lambda provider: "",
        get_provider_default_host=lambda provider: "http://localhost:11434" if provider == "Ollama" else "",
        get_provider_default_model=lambda provider, service: {
            ("Ollama", "translation"): "llama3.2",
            ("HuggingFace", "translation"): "Qwen/Qwen2.5-72B-Instruct",
        }.get((provider, service), ""),
        require_provider_default_host=lambda provider: "http://localhost:11434" if provider == "Ollama" else "",
        require_provider_default_model=lambda provider, service: {
            ("Ollama", "translation"): "llama3.2",
            ("HuggingFace", "translation"): "Qwen/Qwen2.5-72B-Instruct",
        }.get((provider, service), ""),
        missing_provider_credentials_message=lambda provider: f"missing credentials for {provider}",
        normalize_provider_name=lambda provider: "Gemini" if "Gemini" in str(provider) else provider,
        provider_requires_credentials=lambda provider: provider != "Ollama",
        service_supports_provider=lambda service, provider: True,
        preload_vault_key=lambda provider, current_value="", key_manager=None: current_value or (
            "vault-key-123" if provider == "Gemini" else ""
        ),
    )
    monkeypatch.setitem(sys.modules, "key_manager", fake_key_manager_module)

    config_path = tmp_path / "config.json"
    config_path.write_text(
        json.dumps(
            {
                "ocr_provider": 2,
                "ocr_api_key": "old-remote-key",
                "translation_context": "",
                "translation_custom_model": "",
            }
        ),
        encoding="utf-8",
    )

    import src.translation_dialog as translation_dialog

    monkeypatch.setattr(
        translation_dialog,
        "get_msg",
        lambda glossario, chiave, lingua: chiave,
    )
    monkeypatch.setattr("config_utils._config_file_path", lambda: str(config_path))

    dlg = translation_dialog.TranslationDialog(None, glossario_data={}, lingua_corrente="it")
    qtbot.addWidget(dlg)

    dlg.combo_prov.setCurrentIndex(dlg.combo_prov.findText("Ollama (Locale/Privato)"))
    assert dlg.txt_api.text() == ""
    assert "localhost" in dlg.txt_api.placeholderText()


def test_translation_dialog_preserves_manual_key_when_loading_from_vault(monkeypatch, tmp_path, qtbot):
    fake_key_manager_module = types.SimpleNamespace(
        KeyManager=lambda: types.SimpleNamespace(
            get_all_keys=lambda provider: ["vault-key-123"] if provider == "Gemini" else []
        ),
        get_provider_base_url=lambda provider: "",
        get_provider_default_host=lambda provider: "http://localhost:11434" if provider == "Ollama" else "",
        get_provider_default_model=lambda provider, service: {
            ("Ollama", "translation"): "llama3.2",
            ("HuggingFace", "translation"): "Qwen/Qwen2.5-72B-Instruct",
        }.get((provider, service), ""),
        require_provider_default_host=lambda provider: "http://localhost:11434" if provider == "Ollama" else "",
        require_provider_default_model=lambda provider, service: {
            ("Ollama", "translation"): "llama3.2",
            ("HuggingFace", "translation"): "Qwen/Qwen2.5-72B-Instruct",
        }.get((provider, service), ""),
        missing_provider_credentials_message=lambda provider: f"missing credentials for {provider}",
        normalize_provider_name=lambda provider: "Gemini" if "Gemini" in str(provider) else provider,
        provider_requires_credentials=lambda provider: provider != "Ollama",
        service_supports_provider=lambda service, provider: True,
    )
    monkeypatch.setitem(sys.modules, "key_manager", fake_key_manager_module)

    config_path = tmp_path / "config.json"
    config_path.write_text(
        json.dumps(
            {
                "ocr_provider": 2,
                "ocr_api_key": "manual-key-999",
                "translation_context": "",
                "translation_custom_model": "",
            }
        ),
        encoding="utf-8",
    )

    import src.translation_dialog as translation_dialog

    monkeypatch.setattr("config_utils._config_file_path", lambda: str(config_path))
    monkeypatch.setattr(
        translation_dialog,
        "get_msg",
        lambda glossario, chiave, lingua: chiave,
    )

    dlg = translation_dialog.TranslationDialog(None, glossario_data={}, lingua_corrente="it")
    qtbot.addWidget(dlg)

    assert dlg.txt_api.text() == "manual-key-999"


def test_translation_dialog_provider_combo_excludes_transkribus(monkeypatch, qtbot):
    import src.translation_dialog as translation_dialog

    monkeypatch.setattr(
        translation_dialog,
        "get_msg",
        lambda glossario, chiave, lingua: chiave,
    )

    dlg = translation_dialog.TranslationDialog(None, glossario_data={}, lingua_corrente="it")
    qtbot.addWidget(dlg)

    providers = [dlg.combo_prov.itemText(i) for i in range(dlg.combo_prov.count())]
    assert "Transkribus (Italian Handwriting HTR)" not in providers


def test_translation_dialog_uses_runtime_default_hints(monkeypatch, qtbot):
    import src.translation_dialog as translation_dialog

    monkeypatch.setattr(
        translation_dialog,
        "get_msg",
        lambda glossario, chiave, lingua: chiave,
    )

    dlg = translation_dialog.TranslationDialog(None, glossario_data={}, lingua_corrente="it")
    qtbot.addWidget(dlg)

    dlg.combo_prov.setCurrentIndex(dlg.combo_prov.findText("Ollama (Locale/Privato)"))
    assert dlg.txt_api.placeholderText() == "http://localhost:11434"
    assert "llama3.2" in dlg.inp_custom_model.placeholderText()

    dlg.combo_prov.setCurrentIndex(dlg.combo_prov.findText("Hugging Face (Inference API)"))
    assert "Qwen/Qwen2.5-72B-Instruct" in dlg.inp_custom_model.placeholderText()


def test_translation_dialog_save_settings_uses_translation_pref_keys(monkeypatch, qtbot):
    import src.translation_dialog as translation_dialog

    written = {}

    monkeypatch.setattr(
        translation_dialog,
        "get_msg",
        lambda glossario, chiave, lingua: chiave,
    )
    monkeypatch.setattr(
        "config_utils._write_config_prefs",
        lambda key, value: written.__setitem__(key, value),
    )

    dlg = translation_dialog.TranslationDialog(None, glossario_data={}, lingua_corrente="it")
    qtbot.addWidget(dlg)

    dlg.txt_api.setText("translation-key-123")
    dlg.combo_prov.setCurrentIndex(1)
    dlg.txt_ctx.setPlainText("contesto")
    dlg.inp_custom_model.setText("custom-model")
    dlg.save_settings()

    assert written["translation_api_key"] == "translation-key-123"
    assert written["translation_provider"] == 1
    assert "ocr_api_key" not in written
    assert "ocr_provider" not in written


def test_translation_dialog_accepts_vault_key_even_if_field_is_empty(monkeypatch, qtbot):
    import src.translation_dialog as translation_dialog

    class FakeWorker:
        def __init__(self, **kwargs):
            self.kwargs = kwargs
            self.finished = types.SimpleNamespace(connect=lambda cb: None)

        def start(self):
            return None

    warnings = []

    monkeypatch.setattr(
        translation_dialog,
        "get_msg",
        lambda glossario, chiave, lingua: chiave,
    )
    fake_key_manager_module = types.SimpleNamespace(
        KeyManager=lambda: types.SimpleNamespace(
            has_keys=lambda provider: provider == "Gemini",
            get_all_keys=lambda provider: ["vault-key-123"] if provider == "Gemini" else [],
        ),
        get_provider_base_url=lambda provider: "",
        get_provider_default_host=lambda provider: "http://localhost:11434" if provider == "Ollama" else "",
        get_provider_default_model=lambda provider, service: "",
        require_provider_default_host=lambda provider: "http://localhost:11434" if provider == "Ollama" else "",
        require_provider_default_model=lambda provider, service: "",
        missing_provider_credentials_message=lambda provider: f"missing credentials for {provider}",
        normalize_provider_name=lambda provider: "Gemini" if "Gemini" in str(provider) else provider,
        provider_requires_credentials=lambda provider: provider != "Ollama",
        service_supports_provider=lambda service, provider: True,
        preload_vault_key=lambda provider, current_value="", key_manager=None: current_value or (
            "vault-key-123" if provider == "Gemini" else ""
        ),
    )
    monkeypatch.setitem(sys.modules, "key_manager", fake_key_manager_module)
    monkeypatch.setattr(translation_dialog.QMessageBox, "warning", lambda *args: warnings.append(args))
    monkeypatch.setattr(translation_dialog, "TranslationWorker", FakeWorker)

    dlg = translation_dialog.TranslationDialog(None, glossario_data={}, lingua_corrente="it")
    qtbot.addWidget(dlg)

    dlg.txt_orig.setPlainText("testo sorgente")
    dlg.txt_api.setText("")
    gemini_idx = next(
        i for i in range(dlg.combo_prov.count())
        if "Gemini" in dlg.combo_prov.itemText(i)
    )
    dlg.combo_prov.setCurrentIndex(gemini_idx)

    dlg.avvia_traduzione()

    assert warnings == []
    assert isinstance(dlg.worker, FakeWorker)
