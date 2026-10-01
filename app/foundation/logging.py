"""Strict safe-metadata projection; never serialize messages, repr or traceback."""

import contextvars
import json
import logging
import math
import uuid
from datetime import UTC, datetime

request_id = contextvars.ContextVar("aap_request_id", default=None)
EVENTS = frozenset(
    {"request_complete", "startup_ok", "startup_refused", "worker_unavailable", "migration_ok"}
)
ID_FIELDS = ("request_id", "run_id", "attempt_id", "dispatch_id")


def safe_id(value):
    if not isinstance(value, str):
        return None
    try:
        return str(uuid.UUID(str(value)))
    except (ValueError, TypeError, AttributeError):
        return None


class SafeJsonFormatter(logging.Formatter):
    def format(self, record):
        event = record.__dict__.get("event")
        payload = {
            "time": datetime.now(UTC).isoformat(),
            "level": record.levelname if record.levelname in logging._nameToLevel else "UNKNOWN",
            "component": "aap" if record.name.startswith("aap") else "dependency",
            "event": event
            if isinstance(event, str) and event in EVENTS
            else "diagnostic_suppressed",
            "engine": "0.0.1-t002",
        }
        for field in ID_FIELDS:
            value = safe_id(
                record.__dict__.get(field, request_id.get() if field == "request_id" else None)
            )
            if value:
                payload[field] = value
        status = record.__dict__.get("status")
        if type(status) is int and 100 <= status <= 599:
            payload["status"] = status
        elapsed = record.__dict__.get("elapsed_ms")
        if type(elapsed) in (int, float) and math.isfinite(elapsed) and 0 <= elapsed <= 86_400_000:
            payload["elapsed_ms"] = round(elapsed, 3)
        if record.exc_info or record.exc_text or record.stack_info:
            payload["error"] = "exception_suppressed"
        return json.dumps(payload, separators=(",", ":"), ensure_ascii=True)
