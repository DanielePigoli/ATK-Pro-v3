import types

import pytest

import src.ai_model_resolver as resolver


@pytest.fixture(autouse=True)
def clear_discovery_cache():
    resolver.clear_model_discovery_cache()
    yield
    resolver.clear_model_discovery_cache()


@pytest.mark.parametrize(
    "message",
    [
        "404 model_not_found",
        "The model does not exist",
        "This model has been deprecated",
        "Model is no longer available",
        "You do not have access to this model",
    ],
)
def test_model_lifecycle_errors_are_recognized(message):
    assert resolver.is_model_lifecycle_error(RuntimeError(message))


@pytest.mark.parametrize(
    "message",
    [
        "429 quota exceeded",
        "401 unauthorized",
        "connection timed out",
        "invalid JSON response",
    ],
)
def test_unrelated_errors_do_not_trigger_model_fallback(message):
    assert not resolver.is_model_lifecycle_error(RuntimeError(message))


def test_unsupported_parameter_is_not_misclassified_as_retired_model():
    error = RuntimeError(
        "Unsupported parameter: 'max_tokens' is not supported with this model"
    )

    assert not resolver.is_model_lifecycle_error(error)


def test_openai_token_limit_parameter_tracks_model_family():
    assert resolver.openai_completion_limit_kwargs("gpt-4.1", 4096) == {
        "max_tokens": 4096
    }
    assert resolver.openai_completion_limit_kwargs("gpt-5.6-terra", 4096) == {
        "max_completion_tokens": 4096
    }
    assert resolver.openai_completion_limit_kwargs("o4-mini", 4096) == {
        "max_completion_tokens": 4096
    }


def test_default_model_recovers_from_retirement_using_discovery():
    calls = []

    def call_model(model):
        calls.append(model)
        if model == "gpt-4o":
            raise RuntimeError("404 model not found")
        return f"ok:{model}"

    def discoverer(provider, api_key, **kwargs):
        assert provider == "OpenAI"
        assert api_key == "secret"
        assert kwargs["force_refresh"] is True
        return [
            {"id": "text-embedding-3-large", "created": 99},
            {"id": "gpt-5.6-sol", "created": 30},
            {"id": "gpt-5.6-terra", "created": 30},
        ]

    result = resolver.execute_with_model_fallback(
        "OpenAI",
        "translation",
        "secret",
        call_model,
        discoverer=discoverer,
    )

    assert result == "ok:gpt-5.6-terra"
    assert calls == ["gpt-4o", "gpt-5.6-terra"]


def test_successful_fallback_is_reused_without_repeating_discovery():
    calls = []
    discovery_calls = 0

    def call_model(model):
        calls.append(model)
        if model == "gpt-4o":
            raise RuntimeError("model not found")
        return model

    def discoverer(*args, **kwargs):
        nonlocal discovery_calls
        discovery_calls += 1
        return [{"id": "gpt-5.6-terra", "created": 30}]

    first = resolver.execute_with_model_fallback(
        "OpenAI",
        "translation",
        "secret",
        call_model,
        discoverer=discoverer,
    )
    second = resolver.execute_with_model_fallback(
        "OpenAI",
        "translation",
        "secret",
        call_model,
        discoverer=discoverer,
    )

    assert first == second == "gpt-5.6-terra"
    assert calls == ["gpt-4o", "gpt-5.6-terra", "gpt-5.6-terra"]
    assert discovery_calls == 1


def test_explicit_model_is_never_replaced():
    discovery_called = False

    def discoverer(*args, **kwargs):
        nonlocal discovery_called
        discovery_called = True
        return [{"id": "gpt-5.6-terra"}]

    with pytest.raises(RuntimeError, match="model not found"):
        resolver.execute_with_model_fallback(
            "OpenAI",
            "translation",
            "secret",
            lambda model: (_ for _ in ()).throw(RuntimeError("model not found")),
            custom_model="user-pinned-model",
            discoverer=discoverer,
        )

    assert discovery_called is False


def test_quota_error_never_triggers_discovery():
    discovery_called = False

    def discoverer(*args, **kwargs):
        nonlocal discovery_called
        discovery_called = True
        return []

    with pytest.raises(RuntimeError, match="quota"):
        resolver.execute_with_model_fallback(
            "OpenAI",
            "translation",
            "secret",
            lambda model: (_ for _ in ()).throw(RuntimeError("429 quota exceeded")),
            discoverer=discoverer,
        )

    assert discovery_called is False


def test_vision_ranking_rejects_text_only_and_specialized_models():
    records = [
        {
            "id": "deepseek-v5-pro",
            "input_modalities": ["text"],
            "created": 300,
        },
        {
            "id": "deepseek-v5-flash",
            "input_modalities": ["text", "image"],
            "created": 200,
        },
        {
            "id": "deepseek-embedding",
            "input_modalities": ["text", "image"],
            "created": 400,
        },
    ]

    ranked = resolver.rank_discovered_models(
        "DeepSeek",
        "ocr",
        records,
        require_vision=True,
    )

    assert ranked == ["deepseek-v5-flash"]


def test_shutdown_and_archived_models_are_excluded():
    records = [
        {"id": "claude-sonnet-old", "shutdown_date": "2020-01-01"},
        {"id": "claude-sonnet-archived", "archived": True},
        {"id": "claude-sonnet-current", "created": 10},
    ]

    assert resolver.rank_discovered_models("Claude", "translation", records) == [
        "claude-sonnet-current"
    ]


def test_openai_vision_heuristic_accepts_current_general_models():
    records = [
        {"id": "gpt-3.5-turbo", "created": 30},
        {"id": "gpt-4.1", "created": 20},
        {"id": "gpt-5.6-terra", "created": 10},
        {"id": "gpt-5.6-codex", "created": 40},
    ]

    ranked = resolver.rank_discovered_models(
        "OpenAI",
        "ocr",
        records,
        require_vision=True,
    )

    assert ranked == ["gpt-5.6-terra", "gpt-4.1"]


def test_http_discovery_uses_provider_catalog_and_cache(monkeypatch):
    captured = {"calls": 0}

    class FakeResponse:
        def raise_for_status(self):
            return None

        def json(self):
            return {"data": [{"id": "future-model", "created": 123}]}

    def fake_get(url, headers, timeout):
        captured.update(
            calls=captured["calls"] + 1,
            url=url,
            headers=headers,
            timeout=timeout,
        )
        return FakeResponse()

    monkeypatch.setattr(resolver.requests, "get", fake_get)

    first = resolver.discover_available_models(
        "DeepSeek",
        "secret",
        base_url="https://api.deepseek.example",
    )
    second = resolver.discover_available_models(
        "DeepSeek",
        "secret",
        base_url="https://api.deepseek.example",
    )

    assert first == second == [{"id": "future-model", "created": 123}]
    assert captured["calls"] == 1
    assert captured["url"] == "https://api.deepseek.example/models"
    assert captured["headers"]["Authorization"] == "Bearer secret"


def test_ollama_discovery_normalizes_local_model_names(monkeypatch):
    response = types.SimpleNamespace(
        raise_for_status=lambda: None,
        json=lambda: {"models": [{"name": "llava:latest"}, {"name": "llama3.2:latest"}]},
    )
    monkeypatch.setattr(resolver.requests, "get", lambda *args, **kwargs: response)

    records = resolver.discover_available_models(
        "Ollama",
        "ollama",
        base_url="http://localhost:11434/v1",
    )

    assert [item["id"] for item in records] == ["llava:latest", "llama3.2:latest"]
