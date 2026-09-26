"""Runtime discovery and controlled fallback for retired AI models.

The configured model remains the fast path. Discovery is performed only after
the provider reports a model-lifecycle error, and never overrides an explicit
model chosen by the user.
"""

from __future__ import annotations

from datetime import date
import hashlib
import logging
import re
import time
from typing import Callable, Iterable

import requests

from key_manager import (
    get_provider_base_url,
    normalize_provider_name,
    require_provider_default_model,
)


_DISCOVERY_CACHE: dict[tuple[str, str, str], tuple[float, list[dict]]] = {}
_RESOLVED_MODEL_CACHE: dict[tuple[str, str, str, str, bool], str] = {}
_CACHE_SECONDS = 3600
_MAX_FALLBACK_ATTEMPTS = 3

_SPECIALIZED_MARKERS = (
    "embedding",
    "moderation",
    "rerank",
    "whisper",
    "transcrib",
    "speech",
    "tts",
    "realtime",
    "audio",
    "dall-e",
    "image-generation",
    "image_generation",
    "computer-use",
    "computer_use",
    "guard",
    "safety",
    "search-preview",
    "search_preview",
    "codex",
)


def is_model_lifecycle_error(error) -> bool:
    """True only for errors that reasonably indicate an unavailable model."""
    text = str(error or "").lower()
    if "unsupported parameter" in text or "unsupported value" in text:
        return False
    direct_markers = (
        "model_not_found",
        "model not found",
        "unknown model",
        "invalid model",
        "model is deprecated",
        "model has been deprecated",
        "model was deprecated",
        "model is decommissioned",
        "model has been retired",
        "model was retired",
    )
    if any(marker in text for marker in direct_markers):
        return True
    mentions_model = "model" in text or "deployment" in text
    availability_markers = (
        "does not exist",
        "not available",
        "no longer available",
        "not supported",
        "do not have access",
        "doesn't have access",
    )
    return mentions_model and any(marker in text for marker in availability_markers)


def openai_completion_limit_kwargs(model, limit) -> dict:
    """Use the token-limit field accepted by the selected OpenAI generation family."""
    model_id = str(model or "").lower()
    if re.match(r"^(?:gpt-(?:[5-9]|[1-9]\d)|o[1-9])", model_id):
        return {"max_completion_tokens": int(limit)}
    return {"max_tokens": int(limit)}


def clear_model_discovery_cache():
    _DISCOVERY_CACHE.clear()
    _RESOLVED_MODEL_CACHE.clear()


def _credential_fingerprint(api_key: str) -> str:
    return hashlib.sha256(str(api_key or "").encode("utf-8")).hexdigest()[:12]


def _models_url(provider: str, base_url: str) -> str:
    base = str(base_url or get_provider_base_url(provider)).rstrip("/")
    if provider == "Claude":
        return "https://api.anthropic.com/v1/models"
    if provider == "Ollama":
        if base.endswith("/v1"):
            base = base[:-3]
        return base.rstrip("/") + "/api/tags"
    return base + "/models"


def _normalize_model_records(payload) -> list[dict]:
    if isinstance(payload, dict):
        records = payload.get("data")
        if not isinstance(records, list):
            records = payload.get("models")
    elif isinstance(payload, list):
        records = payload
    else:
        records = []

    normalized = []
    for item in records or []:
        if isinstance(item, str):
            item = {"id": item}
        if not isinstance(item, dict):
            continue
        model_id = item.get("id") or item.get("name") or item.get("model")
        if not model_id:
            continue
        record = dict(item)
        record["id"] = str(model_id).replace("models/", "", 1)
        normalized.append(record)
    return normalized


def discover_available_models(
    provider,
    api_key,
    *,
    base_url=None,
    timeout=12,
    force_refresh=False,
) -> list[dict]:
    """Return the models visible to the current credential, cached for one hour."""
    provider_name = normalize_provider_name(provider)
    resolved_base = str(base_url or get_provider_base_url(provider_name) or "")
    cache_key = (
        provider_name,
        resolved_base,
        _credential_fingerprint(api_key),
    )
    cached = _DISCOVERY_CACHE.get(cache_key)
    if cached and not force_refresh and time.monotonic() - cached[0] < _CACHE_SECONDS:
        return [dict(item) for item in cached[1]]

    if provider_name == "Gemini":
        try:
            import google.generativeai as genai
        except ImportError as exc:
            raise RuntimeError("google-generativeai non installato") from exc
        genai.configure(api_key=api_key)
        records = []
        for model in genai.list_models():
            methods = list(getattr(model, "supported_generation_methods", []) or [])
            if "generateContent" not in methods:
                continue
            records.append(
                {
                    "id": str(getattr(model, "name", "")).replace("models/", "", 1),
                    "supported_generation_methods": methods,
                }
            )
    else:
        headers = {"Accept": "application/json"}
        if provider_name == "Claude":
            headers.update(
                {
                    "x-api-key": str(api_key),
                    "anthropic-version": "2023-06-01",
                }
            )
        elif provider_name != "Ollama":
            headers["Authorization"] = f"Bearer {api_key}"
        response = requests.get(
            _models_url(provider_name, resolved_base),
            headers=headers,
            timeout=timeout,
        )
        response.raise_for_status()
        records = _normalize_model_records(response.json())

    records = [item for item in records if item.get("id")]
    _DISCOVERY_CACHE[cache_key] = (time.monotonic(), [dict(item) for item in records])
    return records


def _explicit_vision_capability(record: dict):
    capabilities = record.get("capabilities")
    if isinstance(capabilities, dict) and isinstance(capabilities.get("vision"), bool):
        return capabilities["vision"]

    for key in (
        "input_modalities",
        "supported_input_modalities",
        "modalities",
    ):
        modalities = record.get(key)
        if isinstance(modalities, dict):
            modalities = modalities.get("input")
        if isinstance(modalities, (list, tuple, set)):
            lowered = {str(item).lower() for item in modalities}
            if "image" in lowered or "vision" in lowered:
                return True
            if lowered:
                return False
    return None


def _supports_vision(provider: str, record: dict) -> bool:
    explicit = _explicit_vision_capability(record)
    if explicit is not None:
        return explicit

    model_id = record["id"].lower()
    if provider == "Claude":
        return model_id.startswith("claude-")
    if provider == "OpenAI":
        return bool(re.match(r"^gpt-(?:4o|4\.1|[5-9])", model_id))
    if provider == "DeepSeek":
        return "flash" in model_id or "vision" in model_id or "-vl" in model_id
    if provider == "Mistral":
        return any(token in model_id for token in ("pixtral", "vision", "ministral"))
    if provider == "xAI":
        return "vision" in model_id or bool(re.match(r"^grok-[4-9]", model_id))
    if provider in ("Groq", "HuggingFace", "Ollama"):
        return any(token in model_id for token in ("vision", "llava", "-vl", "_vl", "ocr"))
    return False


def _is_shutdown(record: dict) -> bool:
    value = record.get("shutdown_date")
    if not value:
        return False
    try:
        return date.fromisoformat(str(value)[:10]) <= date.today()
    except ValueError:
        return False


def _preference_score(provider: str, model_id: str, service: str) -> int:
    lowered = model_id.lower()
    preferences = {
        "OpenAI": ("terra", "mini", "chat-latest", "gpt-"),
        "Claude": ("sonnet", "opus", "haiku"),
        "DeepSeek": ("flash", "pro"),
        "Mistral": ("medium", "large", "small", "pixtral", "ministral"),
        "xAI": ("grok",),
        "Groq": ("llama", "qwen", "gemma"),
        "HuggingFace": ("qwen", "llama", "mistral"),
        "Ollama": ("llava", "qwen", "llama") if service == "ocr" else ("llama", "qwen", "mistral"),
        "Gemini": ("flash", "pro"),
    }.get(provider, ())
    for index, token in enumerate(preferences):
        if token in lowered:
            return len(preferences) - index
    return 0


def rank_discovered_models(
    provider,
    service_name,
    records: Iterable[dict],
    *,
    require_vision=False,
) -> list[str]:
    """Filter specialized models and rank stable, general-purpose aliases first."""
    provider_name = normalize_provider_name(provider)
    service = str(service_name or "").strip().lower().replace("-", "_")
    candidates = []
    for record in records:
        if not isinstance(record, dict) or not record.get("id"):
            continue
        model_id = str(record["id"])
        lowered = model_id.lower()
        if record.get("archived") is True or _is_shutdown(record):
            continue
        if any(marker in lowered for marker in _SPECIALIZED_MARKERS):
            continue
        if service != "ocr" and re.search(r"(^|[-_/])ocr($|[-_/])", lowered):
            continue
        if require_vision and not _supports_vision(provider_name, record):
            continue

        versions = tuple(int(part) for part in re.findall(r"\d+", lowered)[:4])
        dated_snapshot = bool(re.search(r"(?:19|20)\d{2}[-_]?[01]\d[-_]?[0-3]\d", lowered))
        try:
            created = int(record.get("created") or 0)
        except (TypeError, ValueError):
            created = 0
        score = (
            _preference_score(provider_name, model_id, service),
            0 if dated_snapshot else 1,
            versions,
            created,
        )
        candidates.append((score, model_id))

    candidates.sort(key=lambda item: item[0], reverse=True)
    return [model_id for _, model_id in candidates]


def execute_with_model_fallback(
    provider,
    service_name,
    api_key,
    call_model: Callable[[str], object],
    *,
    custom_model=None,
    base_url=None,
    require_vision=False,
    discoverer=discover_available_models,
):
    """Execute once with the configured model, then recover from retirement only."""
    provider_name = normalize_provider_name(provider)
    service_key = str(service_name or "").strip().lower().replace("-", "_")
    resolution_key = (
        provider_name,
        service_key,
        str(base_url or get_provider_base_url(provider_name) or ""),
        _credential_fingerprint(api_key),
        bool(require_vision),
    )
    if custom_model and str(custom_model).strip():
        selected_model = str(custom_model).strip()
    else:
        selected_model = _RESOLVED_MODEL_CACHE.get(resolution_key)
        if not selected_model:
            selected_model = require_provider_default_model(provider_name, service_key)
    try:
        return call_model(selected_model)
    except Exception as initial_error:
        if custom_model or not is_model_lifecycle_error(initial_error):
            raise
        _RESOLVED_MODEL_CACHE.pop(resolution_key, None)

        try:
            records = discoverer(
                provider_name,
                api_key,
                base_url=base_url,
                force_refresh=True,
            )
        except Exception as discovery_error:
            logging.warning(
                "[AI-MODEL] Discovery non disponibile per %s: %s",
                provider_name,
                type(discovery_error).__name__,
            )
            raise initial_error

        candidates = rank_discovered_models(
            provider_name,
            service_name,
            records,
            require_vision=require_vision,
        )
        candidates = [item for item in candidates if item != selected_model]
        if not candidates:
            raise initial_error

        last_model_error = initial_error
        for fallback_model in candidates[:_MAX_FALLBACK_ATTEMPTS]:
            logging.warning(
                "[AI-MODEL] %s non disponibile; nuovo tentativo %s con %s.",
                selected_model,
                provider_name,
                fallback_model,
            )
            try:
                result = call_model(fallback_model)
                _RESOLVED_MODEL_CACHE[resolution_key] = fallback_model
                return result
            except Exception as fallback_error:
                if not is_model_lifecycle_error(fallback_error):
                    raise
                last_model_error = fallback_error
                selected_model = fallback_model
        raise last_model_error
