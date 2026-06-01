import logging
from logging.handlers import RotatingFileHandler
import os
from typing import Any, Dict, Optional
import json

LOG_DIR = os.path.join(os.path.dirname(__file__), "..", "logs")
os.makedirs(LOG_DIR, exist_ok=True)
LOG_PATH = os.path.join(LOG_DIR, "trading.log")

_DEFAULT_FMT = "%(asctime)s %(levelname)s %(name)s %(message)s"
_ISO_TIME = "%Y-%m-%dT%H:%M:%S%z"


def _get_formatter() -> logging.Formatter:
    return logging.Formatter(fmt=_DEFAULT_FMT, datefmt=_ISO_TIME)


def _mask_headers(headers: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    if not headers:
        return {}
    masked = {}
    for k, v in headers.items():
        kl = k.lower()
        if "api" in kl or "secret" in kl or "authorization" in kl or "x-mbx-apikey" in kl:
            masked[k] = "<REDACTED>"
        else:
            masked[k] = v
    return masked


def _truncate(text: str, limit: int = 2000) -> str:
    if not isinstance(text, str):
        try:
            text = json.dumps(text, default=str)
        except Exception:
            text = str(text)
    return text if len(text) <= limit else text[:limit] + "...[truncated]"


def _ensure_handlers(logger: logging.Logger, level: int) -> None:
    if logger.handlers:
        return
    logger.setLevel(level)
    formatter = _get_formatter()

    fh = RotatingFileHandler(LOG_PATH, maxBytes=5_000_000, backupCount=5, encoding="utf-8")
    fh.setFormatter(formatter)
    fh.setLevel(level)

    ch = logging.StreamHandler()
    ch.setFormatter(formatter)
    ch.setLevel(level)

    logger.addHandler(fh)
    logger.addHandler(ch)
    logger.propagate = False


def get_logger(name: str = "trading", level: int = logging.INFO) -> logging.Logger:
    """
    Get a configured logger for the trading bot.
    Writes to logs/trading.log and to console. Handlers are idempotent.
    """
    logger = logging.getLogger(name)
    _ensure_handlers(logger, level)
    return logger


# Convenience helpers to consistently log API requests/responses and validation failures.
def log_api_request(logger: logging.Logger, method: str, url: str, headers: Optional[Dict[str, Any]] = None,
                    params: Optional[Dict[str, Any]] = None, body: Optional[Any] = None) -> None:
    """
    Log an outgoing API request. Secrets in headers are redacted.
    """
    try:
        logger.info("API REQUEST method=%s url=%s headers=%s params=%s body=%s",
                    method,
                    url,
                    _mask_headers(headers),
                    _truncate(params or {}),
                    _truncate(body or ""))
    except Exception:
        logger.exception("Failed to log API request")


def log_api_response(logger: logging.Logger, response: Any) -> None:
    """
    Log an HTTP response object from `requests` or similar.
    Will redact sensitive headers and truncate large bodies.
    """
    try:
        status = getattr(response, "status_code", None)
        url = getattr(response, "url", None)
        headers = dict(getattr(response, "headers", {}) or {})
        text = getattr(response, "text", None)
        logger.info("API RESPONSE url=%s status=%s headers=%s body=%s",
                    url,
                    status,
                    _mask_headers(headers),
                    _truncate(text or ""))
    except Exception:
        logger.exception("Failed to log API response")


def log_validation_failure(logger: logging.Logger, field: str, message: str, payload: Optional[Any] = None) -> None:
    """
    Log input validation failures with context.
    """
    try:
        logger.warning("VALIDATION FAILED field=%s message=%s payload=%s",
                       field, message, _truncate(payload or {}))
    except Exception:
        logger.exception("Failed to log validation failure")