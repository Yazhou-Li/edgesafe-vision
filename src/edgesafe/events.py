"""Normalized event contract for edge-AI integrations.

Adapters can translate Frigate, MQTT, webhook or custom detector output into
this small schema before business rules consume it. Keeping the contract
detector-agnostic makes rules testable and integration code replaceable.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Mapping, Optional


class EventType(str, Enum):
    PERSON = "person"
    FIRE = "fire"
    SMOKE = "smoke"
    CAMERA_OFFLINE = "camera_offline"
    CAMERA_ONLINE = "camera_online"
    CUSTOM = "custom"


@dataclass(frozen=True)
class EdgeEvent:
    event_id: str
    camera_id: str
    event_type: EventType
    observed_at: float
    confidence: Optional[float] = None
    track_id: Optional[str] = None
    attributes: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.event_id.strip():
            raise ValueError("event_id is required")
        if not self.camera_id.strip():
            raise ValueError("camera_id is required")
        if self.observed_at < 0:
            raise ValueError("observed_at must be >= 0")
        if self.confidence is not None and not 0 <= self.confidence <= 1:
            raise ValueError("confidence must be between 0 and 1")

    def to_dict(self) -> dict[str, Any]:
        return {
            "eventId": self.event_id,
            "cameraId": self.camera_id,
            "type": self.event_type.value,
            "observedAt": self.observed_at,
            "confidence": self.confidence,
            "trackId": self.track_id,
            "attributes": dict(self.attributes),
        }
