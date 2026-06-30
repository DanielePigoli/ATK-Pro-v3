import json
import sys
import types


def test_ocr_dialog_clears_remote_key_when_ollama_is_selected(monkeypatch, tmp_path, qtbot):
    fake_key_manager_module = types.SimpleNamespace(
        KeyManager=lambda: types.SimpleNamespace(
            get_all_keys=lambda provider: ["vault-key-123"] if provider == "Gemini" else []
        ),
        missing_provider_credentials_message=lambda provider: f"missing credentials for {provider}",
        preload_vault_key=lambda provider, current_value="", key_manager=None: current_value or (
            "vault-key-123" if provider == "Gemini" else ""
        ),
    )
    monkeypatch.setitem(sys.modules, "key_manager", fake_key_manager_module)

    config_path = tmp_path / "config.json"
    config_path.write_text(
        json.dumps(
            {
                "ocr_provider": 0,
                "ocr_api_key": "old-remote-key",
                "ocr_doc_type": "",
                "ocr_custom_prompt": "",
                "ocr_example_text": "",
                "ocr_custom_model": "",
            }
        ),
        encoding="utf-8",
    )

    import src.ocr_dialog as ocr_dialog

    monkeypatch.setattr("config_utils._config_file_path", lambda: str(config_path))
    monkeypatch.setattr(
        ocr_dialog,
        "get_msg",
        lambda glossario, chiave, lingua: chiave,
    )

    dlg = ocr_dialog.AdvancedOCRDialog(None, glossario_data={}, lingua="it")
    qtbot.addWidget(dlg)

    dlg.combo_prov.setCurrentIndex(dlg.combo_prov.findText("Ollama (Locale/Privato)"))

    assert dlg.txt_api.text() == ""
    assert "localhost" in dlg.txt_api.placeholderText()


def test_ocr_dialog_preserves_manual_key_when_loading_from_vault(monkeypatch, tmp_path, qtbot):
    fake_key_manager_module = types.SimpleNamespace(
        KeyManager=lambda: types.SimpleNamespace(
            get_all_keys=lambda provider: ["vault-key-123"] if provider == "Gemini" else []
        ),
        missing_provider_credentials_message=lambda provider: f"missing credentials for {provider}",
        preload_vault_key=lambda provider, current_value="", key_manager=None: current_value or (
            "vault-key-123" if provider == "Gemini" else ""
        ),
    )
    monkeypatch.setitem(sys.modules, "key_manager", fake_key_manager_module)

    config_path = tmp_path / "config.json"
    config_path.write_text(
        json.dumps(
            {
                "ocr_provider": 0,
                "ocr_api_key": "manual-key-999",
                "ocr_doc_type": "",
                "ocr_custom_prompt": "",
                "ocr_example_text": "",
                "ocr_custom_model": "",
            }
        ),
        encoding="utf-8",
    )

    import src.ocr_dialog as ocr_dialog

    monkeypatch.setattr("config_utils._config_file_path", lambda: str(config_path))
    monkeypatch.setattr(
        ocr_dialog,
        "get_msg",
        lambda glossario, chiave, lingua: chiave,
    )

    dlg = ocr_dialog.AdvancedOCRDialog(None, glossario_data={}, lingua="it")
    qtbot.addWidget(dlg)

    assert dlg.txt_api.text() == "manual-key-999"


def test_ocr_dialog_provider_combo_includes_transkribus(monkeypatch, qtbot):
    import src.ocr_dialog as ocr_dialog

    monkeypatch.setattr(
        ocr_dialog,
        "get_msg",
        lambda glossario, chiave, lingua: chiave,
    )

    dlg = ocr_dialog.AdvancedOCRDialog(None, glossario_data={}, lingua="it")
    qtbot.addWidget(dlg)

    providers = [dlg.combo_prov.itemText(i) for i in range(dlg.combo_prov.count())]
    assert "Transkribus (Italian Handwriting HTR)" in providers
