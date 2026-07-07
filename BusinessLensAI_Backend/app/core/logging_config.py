"""
BusinessLens AI — Structured Logging with PII Redaction

Configures a JSON-structured logger that:
- Emits structured JSON in production
- Emits readable text in development
- Redacts sensitive fields (passwords, tokens, API keys, etc.)
- Attaches request_id to every log record
"""

from __future__ import annotations

import logging
import logging.config
import re
from typing import Any

from app.core.config import settings

# ------------------------------------------------------------------ #
# PII / Credential Redaction
# ------------------------------------------------------------------ #

_SENSITIVE_KEYS_RE = re.compile(
    r"(password|secret|token|key|fernet|credential|api_key|authorization)",
    re.IGNORECASE,
)

_SENSITIVE_VALUES_RE = re.compile(
    r"(Bearer\s+\S+|sk-\w+|AIza\S+)"
)


class RedactingFilter(logging.Filter):
    """
    Log filter that scrubs sensitive values from log records.
    Operates on the formatted message string — catches most accidental leaks.
    """

    def filter(self, record: logging.LogRecord) -> bool:
        if isinstance(record.msg, str):
            record.msg = _SENSITIVE_VALUES_RE.sub("[REDACTED]", record.msg)
        if record.args:
            record.args = self._redact_args(record.args)
        return True

    def _redact_args(self, args: Any) -> Any:
        if isinstance(args, dict):
            return {
                k: "[REDACTED]" if _SENSITIVE_KEYS_RE.search(str(k)) else v
                for k, v in args.items()
            }
        if isinstance(args, (list, tuple)):
            return type(args)(self._redact_args(a) for a in args)
        return args


# ------------------------------------------------------------------ #
# Logging Configuration
# ------------------------------------------------------------------ #

def setup_logging() -> None:
    """
    Configure application logging.
    Call once during startup (from app/main.py lifespan).
    """
    log_level = "DEBUG" if settings.DEBUG else "INFO"

    logging.config.dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "filters": {
                "redacting": {
                    "()": RedactingFilter,
                }
            },
            "formatters": {
                "json": {
                    "()": _JsonFormatter,
                },
                "readable": {
                    "format": (
                        "%(asctime)s | %(levelname)-8s | %(name)s:%(lineno)d | %(message)s"
                    ),
                    "datefmt": "%Y-%m-%d %H:%M:%S",
                },
            },
            "handlers": {
                "console": {
                    "class": "logging.StreamHandler",
                    "formatter": "readable" if settings.DEBUG else "json",
                    "filters": ["redacting"],
                    "stream": "ext://sys.stdout",
                },
            },
            "root": {
                "level": log_level,
                "handlers": ["console"],
            },
            "loggers": {
                # Quieten noisy third-party loggers
                "sqlalchemy.engine": {"level": "WARNING", "propagate": True},
                "sqlalchemy.pool": {"level": "WARNING", "propagate": True},
                "uvicorn.access": {"level": "WARNING", "propagate": True},
                "httpx": {"level": "WARNING", "propagate": True},
            },
        }
    )


# ------------------------------------------------------------------ #
# JSON Formatter
# ------------------------------------------------------------------ #

class _JsonFormatter(logging.Formatter):
    """Minimal JSON log formatter (avoids heavy dependencies like python-json-logger)."""

    def format(self, record: logging.LogRecord) -> str:
        import json
        from datetime import UTC, datetime

        payload = {
            "timestamp": datetime.now(UTC).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "line": record.lineno,
        }
        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)
        # Attach any extra context added by middleware (e.g. request_id)
        for key in ("request_id", "user_id", "organization_id"):
            if hasattr(record, key):
                payload[key] = getattr(record, key)
        return json.dumps(payload)


# ------------------------------------------------------------------ #
# Logger Factory
# ------------------------------------------------------------------ #

def get_logger(name: str) -> logging.Logger:
    """Convenience wrapper — use this instead of logging.getLogger directly."""
    return logging.getLogger(name)
