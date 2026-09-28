"""Zone intrusion reference logic for EdgeSafe Vision.

Coordinates are normalized to the range [0, 1] so rules are independent of
camera resolution. The engine consumes tracked person centroids and applies
persistence/cooldown rules before emitting an alarm decision.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, Optional, Sequence, Tuple

from .rules import RuleDecision

Point = Tuple[float, float]


def point_in_polygon(point: Point, polygon: Sequence[Point]) -> bool:
    """Return True when *point* lies inside *polygon* using ray casting."""
    if len(polygon) < 3:
        raise ValueError("polygon must contain at least three points")

    x, y = point
    if not (0 <= x <= 1 and 0 <= y <= 1):
        raise ValueError("point coordinates must be normalized to [0, 1]")

    for px, py in polygon:
        if not (0 <= px <= 1 and 0 <= py <= 1):
            raise ValueError("polygon coordinates must be normalized to [0, 1]")

    inside = False
    j = len(polygon) - 1
    for i in range(len(polygon)):
        xi, yi = polygon[i]
        xj, yj = polygon[j]
        intersects = ((yi > y) != (yj > y)) and (
            x < (xj - xi) * (y - yi) / ((yj - yi) or 1e-12) + xi
        )
        if intersects:
            inside = not inside
        j = i
    return inside


@dataclass(frozen=True)
class ZoneIntrusionRule:
    rule_id: str
    camera_id: str
    polygon: Sequence[Point]
    duration_seconds: float = 3.0
    cooldown_seconds: float = 30.0

    def __post_init__(self) -> None:
        if len(self.polygon) < 3:
            raise ValueError("polygon must contain at least three points")
        if self.duration_seconds < 0:
            raise ValueError("duration_seconds must be >= 0")
        if self.cooldown_seconds < 0:
            raise ValueError("cooldown_seconds must be >= 0")


@dataclass
class _TrackState:
    entered_at: Optional[float] = None
    last_triggered_at: Optional[float] = None
    active: bool = False


class ZoneIntrusionEngine:
    def __init__(self) -> None:
        self._tracks: Dict[Tuple[str, str], _TrackState] = {}

    def evaluate(
        self,
        rule: ZoneIntrusionRule,
        *,
        track_id: str,
        centroid: Point,
        timestamp: float,
    ) -> RuleDecision:
        key = (rule.rule_id, str(track_id))
        state = self._tracks.setdefault(key, _TrackState())

        if not point_in_polygon(centroid, rule.polygon):
            state.entered_at = None
            state.active = False
            return RuleDecision.CLEAR

        if state.last_triggered_at is not None:
            elapsed = timestamp - state.last_triggered_at
            if elapsed < rule.cooldown_seconds:
                return RuleDecision.COOLDOWN

        if state.entered_at is None:
            state.entered_at = timestamp

        if timestamp - state.entered_at < rule.duration_seconds:
            return RuleDecision.PENDING

        if not state.active:
            state.active = True
            state.last_triggered_at = timestamp
            return RuleDecision.TRIGGERED

        return RuleDecision.COOLDOWN

    def prune_tracks(self, live_track_ids: Iterable[str], rule_id: str) -> None:
        live = {str(x) for x in live_track_ids}
        stale = [
            key for key in self._tracks
            if key[0] == rule_id and key[1] not in live
        ]
        for key in stale:
            self._tracks.pop(key, None)
