"""EdgeSafe Vision community reference package."""

from .adapters import (
    UnsupportedMqttMessage,
    parse_frigate_event,
    parse_frigate_mqtt_message,
    parse_normalized_mqtt_event,
)
from .alarms import Alarm, AlarmState
from .events import EdgeEvent, EventType
from .freshness import FreshnessMonitor, FreshnessPolicy, FreshnessReport
from .rules import OccupancyRule, OccupancyRuleEngine, RuleDecision
from .zones import ZoneIntrusionEngine, ZoneIntrusionRule, point_in_polygon

__all__ = [
    "Alarm",
    "UnsupportedMqttMessage",
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
    "parse_frigate_event",
    "parse_frigate_mqtt_message",
    "parse_normalized_mqtt_event",
    "point_in_polygon",
]
