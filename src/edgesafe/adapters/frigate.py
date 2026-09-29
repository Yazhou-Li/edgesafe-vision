"""Frigate event adapter.

The adapter converts Frigate event messages into EdgeSafe Vision's small
detector-agnostic EdgeEvent contract. It extracts only reusable fields instead
of retaining an entire production payload.
"""

from __future__ import annotations

import json
from collections.abc import Mapping
from typing import Any

from ..events import EdgeEvent, EventType


def _load_object(payload: Mapping[str, Any] | str | bytes) -> Mapping[str, Any]:
    if isinstance(payload, bytes):
        try:
            payload = payload.decode("utf-8")
        except UnicodeDecodeError as exc:
            raise ValueError("payload must be UTF-8") from exc

    if isinstance(payload, str):
        try:
            decoded = json.loads(payload)
        except json.JSONDecodeError as exc:
            raise ValueError("payload must contain valid JSON") from exc
    else:
        decoded = payload

    if not isinstance(decoded, Mapping):
        raise ValueError("payload must be a JSON object")

    return decoded


def _required_text(data: Mapping[str, Any], key: str) -> str:
    value = data.get(key)
    if value is None or not str(value).strip():
        raise ValueError(f"Frigate event is missing required field: {key}")
    return str(value)


def _event_type(label: str) -> EventType:
    normalized = label.strip().lower()
    return {
        "person": EventType.PERSON,
        "fire": EventType.FIRE,
        "smoke": EventType.SMOKE,
    }.get(normalized, EventType.CUSTOM)


def _number(value: Any) -> float | None:
    if value is None or isinstance(value, bool):
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _observed_at(data: Mapping[str, Any], lifecycle: str) -> float:
    candidates: list[Any] = []

    if lifecycle == "end":
        candidates.append(data.get("end_time"))

    candidates.extend(
        [
            data.get("frame_time"),
            data.get("start_time"),
            data.get("end_time"),
        ]
    )

    snapshot = data.get("snapshot")
    if isinstance(snapshot, Mapping):
        candidates.append(snapshot.get("frame_time"))

    for value in candidates:
        number = _number(value)
        if number is not None and number >= 0:
            return number

    raise ValueError("Frigate event does not contain a usable timestamp")


def _confidence(data: Mapping[str, Any]) -> float | None:
    snapshot = data.get("snapshot")
    snapshot_score = snapshot.get("score") if isinstance(snapshot, Mapping) else None

    for value in (data.get("score"), data.get("top_score"), snapshot_score):
        number = _number(value)
        if number is None:
            continue
        if not 0 <= number <= 1:
            raise ValueError("Frigate confidence must be between 0 and 1")
        return number

    return None


def parse_frigate_event(
    payload: Mapping[str, Any] | str | bytes,
) -> EdgeEvent:
    """Convert a Frigate events message into an EdgeEvent.

    Frigate publishes new, update and end messages. The adapter prefers the
    after object and falls back to before for defensive compatibility with
    synthetic or partial test payloads.
    """

    root = _load_object(payload)
    lifecycle = str(root.get("type") or "update").strip().lower()

    if lifecycle not in {"new", "update", "end"}:
        raise ValueError("Frigate event type must be new, update, or end")

    body = root.get("after")
    if not isinstance(body, Mapping):
        body = root.get("before")
    if not isinstance(body, Mapping):
        raise ValueError("Frigate event must contain an after or before object")

    event_id = _required_text(body, "id")
    camera_id = _required_text(body, "camera")
    label = _required_text(body, "label")

    attributes: dict[str, Any] = {
        "source": "frigate",
        "lifecycle": lifecycle,
        "label": label,
    }

    selected_fields = {
        "current_zones": "currentZones",
        "entered_zones": "enteredZones",
        "sub_label": "subLabel",
        "box": "box",
        "area": "area",
        "stationary": "stationary",
        "false_positive": "falsePositive",
    }

    for source_key, target_key in selected_fields.items():
        if source_key in body:
            attributes[target_key] = body[source_key]

    snapshot = body.get("snapshot")
    if isinstance(snapshot, Mapping):
        if "box" in snapshot and "box" not in body:
            attributes["box"] = snapshot["box"]
        if "area" in snapshot and "area" not in body:
            attributes["area"] = snapshot["area"]

    return EdgeEvent(
        event_id=event_id,
        camera_id=camera_id,
        event_type=_event_type(label),
        observed_at=_observed_at(body, lifecycle),
        confidence=_confidence(body),
        track_id=event_id,
        attributes=attributes,
    )
