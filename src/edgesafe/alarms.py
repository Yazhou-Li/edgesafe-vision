"""A small, auditable alarm lifecycle model.

The Community Edition keeps alarm state transitions explicit so they can be
tested independently of any web framework or database.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Optional


class AlarmState(str, Enum):
    OPEN = "open"
    ACKNOWLEDGED = "acknowledged"
    RESOLVED = "resolved"


@dataclass
class Alarm:
    alarm_id: str
    rule_id: str
    camera_id: str
    opened_at: float
    state: AlarmState = AlarmState.OPEN
    acknowledged_at: Optional[float] = None
    resolved_at: Optional[float] = None

    def acknowledge(self, timestamp: float) -> None:
        if self.state == AlarmState.RESOLVED:
            raise ValueError("resolved alarm cannot be acknowledged")
        if timestamp < self.opened_at:
            raise ValueError("acknowledgement cannot predate alarm")
        self.state = AlarmState.ACKNOWLEDGED
        self.acknowledged_at = timestamp

    def resolve(self, timestamp: float) -> None:
        if timestamp < self.opened_at:
            raise ValueError("resolution cannot predate alarm")
        if self.acknowledged_at is not None and timestamp < self.acknowledged_at:
            raise ValueError("resolution cannot predate acknowledgement")
        self.state = AlarmState.RESOLVED
        self.resolved_at = timestamp
