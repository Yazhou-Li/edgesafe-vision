"""Integration adapters for external edge-AI event sources."""

from .frigate import parse_frigate_event
from .webhook import parse_webhook_event
from .mqtt import (
    UnsupportedMqttMessage,
    parse_frigate_mqtt_message,
    parse_normalized_mqtt_event,
)

__all__ = [
    "UnsupportedMqttMessage",
    "parse_frigate_event",
    "parse_frigate_mqtt_message",
    "parse_normalized_mqtt_event",
    "parse_webhook_event",
]
