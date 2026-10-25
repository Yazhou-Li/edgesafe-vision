"""Shared conversion for EdgeSafe-normalized event mappings."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from ..events import EdgeEvent, EventType


def normalized_event_from_mapping(
    data: Mapping[str, Any],
    *,
    label: str = "normalized event",
) -> EdgeEvent:
    """Convert the documented normalized event mapping into an EdgeEvent."""
    try:
        event_type = EventType(str(data["type"]))
        event_id = str(data["eventId"])
        camera_id = str(data["cameraId"])
        observed_at = float(data["observedAt"])
    except KeyError as exc:
        raise ValueError(f"{label} is missing {exc.args[0]}") from exc
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{label} contains an invalid core field") from exc

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
