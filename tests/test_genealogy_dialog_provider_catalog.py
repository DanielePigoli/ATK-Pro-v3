import json


def test_genealogy_provider_catalog_helpers_filter_from_ai_search_catalog(tmp_path):
    from src.genealogy_dialog import (
        get_genealogy_fallback_providers,
        get_genealogy_service_providers,
    )
    from src.key_manager import get_service_providers

    class FakeKM:
        def get_all_keys(self, provider):
            return {
                "Gemini": ["g-key"],
                "Claude": ["c-key"],
                "Ollama": ["http://localhost:11434"],
            }.get(provider, [])

    assert get_genealogy_service_providers() == list(get_service_providers("ai_search"))
    assert get_genealogy_fallback_providers(FakeKM(), "Gemini") == ["Claude", "Ollama"]


def test_genealogy_dialog_uses_provider_catalog_and_runtime_default_hint(monkeypatch, tmp_path, qtbot):
    import src.genealogy_dialog as genealogy_dialog
    from src.key_manager import get_service_providers

    config_path = tmp_path / "config.json"
    config_path.write_text(json.dumps({}), encoding="utf-8")
    presets_path = tmp_path / "genealogy_presets.json"
    presets_path.write_text("{}", encoding="utf-8")

    monkeypatch.setattr("config_utils._config_file_path", lambda: str(config_path))
    monkeypatch.setattr(genealogy_dialog, "PRESETS_FILE", str(presets_path))
    monkeypatch.setattr(genealogy_dialog.GenealogyDialog, "gm", lambda self, text: text)

    dlg = genealogy_dialog.GenealogyDialog(None, glossario={})
    qtbot.addWidget(dlg)

    providers = [dlg.combo_provider.itemText(i) for i in range(dlg.combo_provider.count())]
    assert providers == list(get_service_providers("ai_search"))

    dlg.combo_provider.setCurrentText("Claude")
    assert "claude-opus-4-5" in dlg.inp_custom_model.placeholderText()

    dlg.combo_provider.setCurrentText("Gemini")
    assert not dlg.inp_custom_model.isVisible()
