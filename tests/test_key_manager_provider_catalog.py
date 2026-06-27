import csv

from src.key_manager import (
    SUPPORTED_AI_PROVIDERS,
    KeyManager,
    normalize_provider_name,
)


def test_default_key_file_contains_all_supported_providers(tmp_path):
    key_file = tmp_path / "api_keys.csv"

    KeyManager(file_path=str(key_file))

    content = key_file.read_text(encoding="utf-8-sig")
    for provider in SUPPORTED_AI_PROVIDERS:
        assert provider in content


def test_existing_key_file_is_extended_without_losing_keys(tmp_path):
    key_file = tmp_path / "api_keys.csv"
    key_file.write_text(
        "sep=;\nProvider;Key;Note\nGemini;gemini-key;old\nClaude;claude-key;old\n",
        encoding="utf-8-sig",
    )

    km = KeyManager(file_path=str(key_file))

    assert km.get_all_keys("Gemini") == ["gemini-key"]
    assert km.get_all_keys("Anthropic") == ["claude-key"]
    rows = list(csv.DictReader(
        key_file.read_text(encoding="utf-8-sig").splitlines()[1:],
        delimiter=";",
    ))
    providers = {row["Provider"] for row in rows}
    assert set(SUPPORTED_AI_PROVIDERS).issubset(providers)


def test_provider_aliases_are_normalized_for_key_lookup_and_rotation(tmp_path):
    key_file = tmp_path / "api_keys.csv"
    key_file.write_text(
        "sep=;\nProvider;Key;Note\nGrok;grok-key;alias\nHugging Face;hf-key;alias\n",
        encoding="utf-8-sig",
    )

    km = KeyManager(file_path=str(key_file))

    assert normalize_provider_name("Grok") == "xAI"
    assert km.get_all_keys("xAI") == ["grok-key"]
    assert km.get_all_keys("HuggingFace") == ["hf-key"]
    assert km.has_keys("Hugging Face")
    assert km.get_next_key("Grok") == ("grok-key", False)


def test_ui_provider_labels_are_known_by_key_manager():
    labels = [
        "Anthropic / Claude (Miglior Testo)",
        "OpenAI (GPT-4o)",
        "Google Gemini",
        "DeepSeek (Economico/Testo)",
        "Mistral",
        "xAI / Grok",
        "Groq (Veloce)",
        "Hugging Face (Inference API)",
        "Ollama (Locale/Privato)",
        "Transkribus (Italian Handwriting HTR)",
    ]

    normalized = {normalize_provider_name(label) for label in labels}

    assert normalized.issubset(set(SUPPORTED_AI_PROVIDERS))
    assert "Transkribus" in normalized
