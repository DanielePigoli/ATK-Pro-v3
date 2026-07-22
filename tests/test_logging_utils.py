import logging

from src.logging_utils import get_default_log_level, is_debug_logging_enabled


def test_debug_logging_flag_is_disabled_by_default(monkeypatch):
    monkeypatch.delenv("ATKPRO_DEBUG_LOGS", raising=False)
    monkeypatch.delenv("ATKPRO_ENV", raising=False)

    assert is_debug_logging_enabled() is False
    assert get_default_log_level() == logging.INFO


def test_debug_logging_flag_enables_debug(monkeypatch):
    monkeypatch.setenv("ATKPRO_DEBUG_LOGS", "1")
    monkeypatch.setenv("ATKPRO_ENV", "production")

    assert is_debug_logging_enabled() is True
    assert get_default_log_level() == logging.DEBUG


def test_production_defaults_to_warning_without_debug_flag(monkeypatch):
    monkeypatch.delenv("ATKPRO_DEBUG_LOGS", raising=False)
    monkeypatch.setenv("ATKPRO_ENV", "production")

    assert get_default_log_level() == logging.WARNING
