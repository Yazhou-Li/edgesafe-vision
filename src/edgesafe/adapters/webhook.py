"""Dependency-free adapter for EdgeSafe-normalized webhook payloads."""

from __future__ import annotations

import json
from collections.abc import Mapping
from typing import Any

from ..events import EdgeEvent, EventType


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
    data = _json_object(payload)
    try:
        event_type = EventType(str(data["type"]))
        event_id = str(data["eventId"])
        camera_id = str(data["cameraId"])
        observed_at = float(data["observedAt"])
    except KeyError as exc:
        raise ValueError(f"webhook event is missing {exc.args[0]}") from exc
    except (TypeError, ValueError) as exc:
        raise ValueError("webhook event contains an invalid core field") from exc

    confidence = data.get("confidence")
    if confidence is not None:
        try:
            confidence = float(confidence)
        except (TypeError, ValueError) as exc:
            raise ValueError("confidence must be numeric") from exc

    attributes = data.get("attributes", {})
    if not isinstance(attributes, Mapping):
        raise ValueError("attributes must be a JSON object")

    track_id = data.get("trackId")
    if track_id is not None:
        track_id = str(track_id)

    return EdgeEvent(
        event_id=event_id,
        camera_id=camera_id,
        event_type=event_type,
        observed_at=observed_at,
        confidence=confidence,
        track_id=track_id,
        attributes=dict(attributes),
    )
