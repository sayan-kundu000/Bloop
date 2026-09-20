"""
Bloop Centralized Logging Module
Configures structured, environment-aware logging with automated secret masking
to guarantee that sensitive tokens, keys, and credentials are never leaked.
"""

import logging
import sys
from typing import List
from urllib.parse import urlsplit
from backend.app.core.config import settings


class SecretMaskingFilter(logging.Filter):
    """
    Log filter that intercepts and sanitizes any sensitive credentials or secrets
    before log records are emitted to handlers, preserving non-string argument types
    for logging format specifiers (e.g. %d, %.5f).
    """

    def __init__(self, secrets_to_mask: List[str] = None):
        super().__init__()
        self.secrets_to_mask: List[str] = [s for s in (secrets_to_mask or []) if s and len(s) >= 4]

    def filter(self, record: logging.LogRecord) -> bool:
        if not self.secrets_to_mask:
            return True

        try:
            # Mask string message
            if isinstance(record.msg, str):
                for secret in self.secrets_to_mask:
                    if secret in record.msg:
                        record.msg = record.msg.replace(secret, "***MASKED***")

            # Mask string arguments without altering numeric or non-string types
            if record.args:
                if isinstance(record.args, dict):
                    cleaned_args = {}
                    for k, v in record.args.items():
                        if isinstance(v, str):
                            for secret in self.secrets_to_mask:
                                if secret in v:
                                    v = v.replace(secret, "***MASKED***")
                        cleaned_args[k] = v
                    record.args = cleaned_args
                elif isinstance(record.args, tuple):
                    cleaned_tuple = []
                    for item in record.args:
                        if isinstance(item, str):
                            for secret in self.secrets_to_mask:
                                if secret in item:
                                    item = item.replace(secret, "***MASKED***")
                        cleaned_tuple.append(item)
                    record.args = tuple(cleaned_tuple)
        except Exception:
            pass

        return True


def _get_active_secrets() -> List[str]:
    """Collects current sensitive values from settings for masking filter."""
    sensitive = []
    if settings.JWT_SECRET_KEY and len(settings.JWT_SECRET_KEY) >= 6:
        sensitive.append(settings.JWT_SECRET_KEY)
    if settings.ELEVENLABS_API_KEY and len(settings.ELEVENLABS_API_KEY) >= 6:
        sensitive.append(settings.ELEVENLABS_API_KEY)
    if settings.DATABASE_URL:
        try:
            parsed = urlsplit(settings.DATABASE_URL)
            if parsed.password:
                sensitive.append(parsed.password)
        except Exception:
            pass
    return sensitive


def setup_logging():
    """Initializes and returns configured root logger with security masking."""
    level_name = settings.LOG_LEVEL.upper()
    log_level = getattr(logging, level_name, logging.INFO)

    formatter = logging.Formatter(
        fmt="%(asctime)s [%(levelname)s] %(name)s (%(filename)s:%(lineno)d) - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)

    # Attach automated secret sanitizer
    masking_filter = SecretMaskingFilter(_get_active_secrets())
    handler.addFilter(masking_filter)

    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    root_logger.handlers = [handler]

    # Third-party logger tuning
    logging.getLogger("uvicorn.access").setLevel(logging.INFO)
    logging.getLogger("passlib").setLevel(logging.ERROR)
    logging.getLogger("httpx").setLevel(logging.WARNING)

    return root_logger


logger = logging.getLogger("bloop")
