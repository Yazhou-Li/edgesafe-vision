"""MQTT message adapters.

These helpers deliberately do not depend on a specific MQTT client library.
Applications can feed topic and payload values from paho-mqtt, asyncio clients,
Home Assistant bridges, test fixtures, or another transport layer.
"""

from __future__ import annotations

import json
import time
from collections.abc import Mapping
from typing import Any

from ..events import EdgeEvent, EventType
from .frigate import parse_frigate_event


class UnsupportedMqttMessage(ValueError):
    """Raised when a topic is outside the adapter's documented contract."""


def _text(payload: str | bytes) -> str:
    if isinstance(payload, bytes):
        try:
            return payload.decode("utf-8").strip()
        except UnicodeDecodeError as exc:
            raise ValueError("MQTT payload must be UTF-8") from exc
    return str(payload).strip()


def _json_object(payload: Mapping[str, Any] | str | bytes) -> Mapping[str, Any]:
    if isinstance(payload, Mapping):
        return payload

    raw = _text(payload)
    try:
        value = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ValueError("MQTT payload must contain valid JSON") from exc

    if not isinstance(value, Mapping):
        raise ValueError("MQTT payload must be a JSON object")

    return value


def parse_normalized_mqtt_event(
    topic: str,
    payload: Mapping[str, Any] | str | bytes,
    *,
    topic_prefix: str = "edgesafe",
) -> EdgeEvent:
    """Parse an EdgeSafe-normalized event from <prefix>/events."""

    expected = f"{topic_prefix.strip('/')}/events"
    if topic.strip("/") != expected:
        raise UnsupportedMqttMessage(
            f"expected topic {expected!r}, got {topic!r}"
        )

    data = _json_object(payload)

    try:
        event_type = EventType(str(data["type"]))
        event_id = str(data["eventId"])
        camera_id = str(data["cameraId"])
        observed_at = float(data["observedAt"])
    except KeyError as exc:
        raise ValueError(f"normalized event is missing {exc.args[0]}") from exc
    except (TypeError, ValueError) as exc:
        raise ValueError("normalized event contains an invalid core field") from exc

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


def parse_frigate_mqtt_message(
    topic: str,
    payload: Mapping[str, Any] | str | bytes,
    *,
    topic_prefix: str = "frigate",
    observed_at: float | None = None,
) -> EdgeEvent:
    """Parse documented Frigate MQTT event and camera-status topics.

    Supported topics are <prefix>/events and
    <prefix>/<camera>/status/<role>.

    Camera role status values online and offline map to explicit camera
    lifecycle events. disabled is preserved as a custom event because it
    represents an intentional state rather than a fault.
    """

    prefix = topic_prefix.strip("/")
    normalized_topic = topic.strip("/")

    if normalized_topic == f"{prefix}/events":
        return parse_frigate_event(payload)

    parts = normalized_topic.split("/")
    if (
        len(parts) == 4
        and parts[0] == prefix
        and parts[2] == "status"
        and parts[1]
        and parts[3]
    ):
        camera_id = parts[1]
        role = parts[3]
        status = _text(payload).lower()

        if status == "online":
            event_type = EventType.CAMERA_ONLINE
        elif status == "offline":
            event_type = EventType.CAMERA_OFFLINE
        elif status == "disabled":
            event_type = EventType.CUSTOM
        else:
            raise ValueError(
                "Frigate camera status must be online, offline, or disabled"
            )

        timestamp = time.time() if observed_at is None else float(observed_at)
        if timestamp < 0:
            raise ValueError("observed_at must be >= 0")

        return EdgeEvent(
            event_id=f"frigate-status:{camera_id}:{role}:{status}",
            camera_id=camera_id,
            event_type=event_type,
            observed_at=timestamp,
            attributes={
                "source": "frigate-mqtt",
                "topic": normalized_topic,
                "role": role,
                "status": status,
            },
        )

    raise UnsupportedMqttMessage(
        f"unsupported Frigate MQTT topic: {topic!r}"
    )
