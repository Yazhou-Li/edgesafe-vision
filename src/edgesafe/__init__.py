"""EdgeSafe Vision community reference package."""

from .alarms import Alarm, AlarmState
from .events import EdgeEvent, EventType
from .freshness import FreshnessMonitor, FreshnessPolicy, FreshnessReport
from .rules import OccupancyRule, OccupancyRuleEngine, RuleDecision
from .zones import ZoneIntrusionEngine, ZoneIntrusionRule, point_in_polygon

__all__ = [
    "Alarm",
    "AlarmState",
    "EdgeEvent",
    "EventType",
    "FreshnessMonitor",
    "FreshnessPolicy",
    "FreshnessReport",
    "OccupancyRule",
    "OccupancyRuleEngine",
    "RuleDecision",
    "ZoneIntrusionEngine",
    "ZoneIntrusionRule",
    "point_in_polygon",
]
