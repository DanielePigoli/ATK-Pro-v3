import json
import sys
import types

from PySide6.QtWidgets import QApplication


def test_translation_dialog_preloads_cassaforte_key(monkeypatch, tmp_path, qtbot):
    fake_key_manager_module = types.SimpleNamespace(
        KeyManager=lambda: types.SimpleNamespace(
            get_all_keys=lambda provider: ["vault-key-123"] if provider == "Gemini" else []
        ),
        missing_provider_credentials_message=lambda provider: f"missing credentials for {provider}",
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
