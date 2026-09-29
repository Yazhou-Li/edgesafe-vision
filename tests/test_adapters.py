import json
import unittest

from edgesafe.adapters import (
    UnsupportedMqttMessage,
    parse_frigate_event,
    parse_frigate_mqtt_message,
    parse_normalized_mqtt_event,
)
from edgesafe.events import EventType


class FrigateAdapterTests(unittest.TestCase):
    def test_person_event_is_normalized(self):
        payload = {
            "type": "new",
            "after": {
                "id": "1700000000.123-demo",
                "camera": "front_door",
                "frame_time": 1700000001.5,
                "label": "person",
                "score": 0.91,
                "current_zones": ["entrance"],
                "box": [100, 120, 260, 420],
            },
        }

        event = parse_frigate_event(payload)

        self.assertEqual(event.event_type, EventType.PERSON)
        self.assertEqual(event.camera_id, "front_door")
        self.assertEqual(event.track_id, "1700000000.123-demo")
        self.assertEqual(event.observed_at, 1700000001.5)
        self.assertEqual(event.confidence, 0.91)
        self.assertEqual(event.attributes["lifecycle"], "new")
        self.assertEqual(event.attributes["currentZones"], ["entrance"])

    def test_end_event_prefers_end_time(self):
        payload = json.dumps(
            {
                "type": "end",
                "after": {
                    "id": "1700000000.123-demo",
                    "camera": "warehouse",
                    "frame_time": 1700000005.0,
                    "end_time": 1700000010.0,
                    "label": "smoke",
                    "top_score": 0.88,
                },
            }
        ).encode("utf-8")

        event = parse_frigate_event(payload)

        self.assertEqual(event.event_type, EventType.SMOKE)
        self.assertEqual(event.observed_at, 1700000010.0)
        self.assertEqual(event.attributes["lifecycle"], "end")

    def test_unknown_label_becomes_custom(self):
        event = parse_frigate_event(
            {
                "type": "update",
                "after": {
                    "id": "evt-car-1",
                    "camera": "parking",
                    "frame_time": 10,
                    "label": "car",
                },
            }
        )
        self.assertEqual(event.event_type, EventType.CUSTOM)
        self.assertEqual(event.attributes["label"], "car")

    def test_missing_after_or_before_is_rejected(self):
        with self.assertRaises(ValueError):
            parse_frigate_event({"type": "new"})


class MqttAdapterTests(unittest.TestCase):
    def test_frigate_events_topic_dispatches(self):
        payload = {
            "type": "new",
            "after": {
                "id": "evt-1",
                "camera": "cam-a",
                "frame_time": 12.5,
                "label": "person",
            },
        }

        event = parse_frigate_mqtt_message("frigate/events", payload)

        self.assertEqual(event.event_type, EventType.PERSON)
        self.assertEqual(event.camera_id, "cam-a")

    def test_camera_status_topics(self):
        offline = parse_frigate_mqtt_message(
            "frigate/cam-a/status/detect",
            b"offline",
            observed_at=42,
        )
        online = parse_frigate_mqtt_message(
            "frigate/cam-a/status/detect",
            "online",
            observed_at=43,
        )
        disabled = parse_frigate_mqtt_message(
            "frigate/cam-a/status/record",
            "disabled",
            observed_at=44,
        )

        self.assertEqual(offline.event_type, EventType.CAMERA_OFFLINE)
        self.assertEqual(online.event_type, EventType.CAMERA_ONLINE)
        self.assertEqual(disabled.event_type, EventType.CUSTOM)
        self.assertEqual(disabled.attributes["status"], "disabled")

    def test_custom_frigate_prefix(self):
        event = parse_frigate_mqtt_message(
            "site-a/cam-1/status/detect",
            "offline",
            topic_prefix="site-a",
            observed_at=1,
        )
        self.assertEqual(event.camera_id, "cam-1")
        self.assertEqual(event.event_type, EventType.CAMERA_OFFLINE)

    def test_unsupported_topic_is_explicit(self):
        with self.assertRaises(UnsupportedMqttMessage):
            parse_frigate_mqtt_message("frigate/cam-a/detect/state", "ON")

    def test_normalized_mqtt_event(self):
        event = parse_normalized_mqtt_event(
            "edgesafe/events",
            {
                "eventId": "EV-42",
                "cameraId": "CAM-42",
                "type": "fire",
                "observedAt": 100.5,
                "confidence": 0.97,
                "trackId": "track-42",
                "attributes": {"source": "synthetic-detector"},
            },
        )

        self.assertEqual(event.event_type, EventType.FIRE)
        self.assertEqual(event.track_id, "track-42")
        self.assertEqual(event.attributes["source"], "synthetic-detector")

    def test_normalized_topic_prefix_is_enforced(self):
        with self.assertRaises(UnsupportedMqttMessage):
            parse_normalized_mqtt_event(
                "other/events",
                {
                    "eventId": "EV-1",
                    "cameraId": "CAM-1",
                    "type": "person",
                    "observedAt": 1,
                },
            )


if __name__ == "__main__":
    unittest.main()
