import unittest

from edgesafe.events import EdgeEvent, EventType


class EdgeEventTests(unittest.TestCase):
    def test_serialization(self):
        event = EdgeEvent(
            event_id="EV-DEMO-001",
            camera_id="CAM-DEMO-01",
            event_type=EventType.PERSON,
            observed_at=10.5,
            confidence=0.93,
            track_id="person-7",
            attributes={"centroid": [0.5, 0.7]},
        )
        payload = event.to_dict()
        self.assertEqual(payload["type"], "person")
        self.assertEqual(payload["cameraId"], "CAM-DEMO-01")
        self.assertEqual(payload["trackId"], "person-7")

    def test_confidence_range(self):
        with self.assertRaises(ValueError):
            EdgeEvent(
                event_id="EV-1",
                camera_id="CAM-1",
                event_type=EventType.SMOKE,
                observed_at=0,
                confidence=1.2,
            )


if __name__ == "__main__":
    unittest.main()
