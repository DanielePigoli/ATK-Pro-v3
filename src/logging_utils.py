import logging
import os


def get_atkpro_env() -> str:
    return os.environ.get("ATKPRO_ENV", "development").strip().lower()


def is_debug_logging_enabled() -> bool:
    value = os.environ.get("ATKPRO_DEBUG_LOGS", "").strip().lower()
    return value in {"1", "true", "yes", "on"}


def get_default_log_level() -> int:
    if is_debug_logging_enabled():
        return logging.DEBUG
    if get_atkpro_env() == "production":
        return logging.WARNING
    return logging.INFO
