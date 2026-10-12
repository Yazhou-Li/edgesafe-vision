"""Dependency-free adapter for EdgeSafe-normalized webhook payloads."""

from __future__ import annotations

import json
from collections.abc import Mapping
from typing import Any

from ..events import EdgeEvent
from .normalized import normalized_event_from_mapping


def _json_object(payload: Mapping[str, Any] | str | bytes) -> Mapping[str, Any]:
    if isinstance(payload, Mapping):
        return payload
    if isinstance(payload, bytes):
        try:
            payload = payload.decode("utf-8")
        except UnicodeDecodeError as exc:
            raise ValueError("webhook payload must be UTF-8") from exc
    if not isinstance(payload, str):
        raise ValueError("webhook payload must be a JSON object, string, or UTF-8 bytes")
    try:
        value = json.loads(payload)
    except json.JSONDecodeError as exc:
        raise ValueError("webhook payload must contain valid JSON") from exc
    if not isinstance(value, Mapping):
        raise ValueError("webhook payload must be a JSON object")
    return value


def parse_webhook_event(payload: Mapping[str, Any] | str | bytes) -> EdgeEvent:
    """Parse the documented normalized webhook payload into an EdgeEvent."""
    return normalized_event_from_mapping(
        _json_object(payload),
        label="webhook event",
    )
