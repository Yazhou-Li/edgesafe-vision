"""Sanitized reference rules for EdgeSafe Vision.

This module is intentionally customer-agnostic. It demonstrates how raw
occupancy observations can be converted into stable alarm state transitions
using threshold, persistence and cooldown controls.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Dict, Optional


class RuleDecision(str, Enum):
    CLEAR = "clear"
    PENDING = "pending"
    TRIGGERED = "triggered"
    COOLDOWN = "cooldown"


@dataclass(frozen=True)
class OccupancyRule:
    rule_id: str
    camera_id: str
    threshold: int
    duration_seconds: float = 3.0
    cooldown_seconds: float = 30.0

    def __post_init__(self) -> None:
        if self.threshold < 1:
            raise ValueError("threshold must be >= 1")
        if self.duration_seconds < 0:
            raise ValueError("duration_seconds must be >= 0")
        if self.cooldown_seconds < 0:
            raise ValueError("cooldown_seconds must be >= 0")


@dataclass
class _RuleState:
    above_since: Optional[float] = None
    last_triggered_at: Optional[float] = None
    active: bool = False


class OccupancyRuleEngine:
    """Evaluate occupancy rules against timestamped observations.

    Timestamps are supplied by the caller, which keeps the engine deterministic
    and straightforward to test.
    """

    def __init__(self) -> None:
        self._states: Dict[str, _RuleState] = {}

    def evaluate(
        self,
        rule: OccupancyRule,
        *,
        person_count: int,
        timestamp: float,
    ) -> RuleDecision:
        if person_count < 0:
            raise ValueError("person_count must be >= 0")

        state = self._states.setdefault(rule.rule_id, _RuleState())

        if person_count < rule.threshold:
            state.above_since = None
            state.active = False
            return RuleDecision.CLEAR

        if state.last_triggered_at is not None:
            elapsed = timestamp - state.last_triggered_at
            if elapsed < rule.cooldown_seconds:
                return RuleDecision.COOLDOWN

        if state.above_since is None:
            state.above_since = timestamp

        sustained_for = timestamp - state.above_since
        if sustained_for < rule.duration_seconds:
            return RuleDecision.PENDING

        if not state.active:
            state.active = True
            state.last_triggered_at = timestamp
            return RuleDecision.TRIGGERED

        return RuleDecision.COOLDOWN

    def reset(self, rule_id: str) -> None:
        self._states.pop(rule_id, None)
