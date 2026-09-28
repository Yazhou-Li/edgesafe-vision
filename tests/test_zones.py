import unittest

from edgesafe.rules import RuleDecision
from edgesafe.zones import (
    ZoneIntrusionEngine,
    ZoneIntrusionRule,
    point_in_polygon,
)


class ZoneTests(unittest.TestCase):
    def setUp(self):
        self.rule = ZoneIntrusionRule(
            rule_id="demo-zone",
            camera_id="CAM-DEMO-02",
            polygon=[
                (0.45, 0.45),
                (0.95, 0.45),
                (0.95, 0.95),
                (0.45, 0.95),
            ],
            duration_seconds=3,
            cooldown_seconds=10,
        )
        self.engine = ZoneIntrusionEngine()

    def test_point_in_polygon(self):
        self.assertTrue(point_in_polygon((0.7, 0.7), self.rule.polygon))
        self.assertFalse(point_in_polygon((0.2, 0.2), self.rule.polygon))

    def test_intrusion_requires_persistence(self):
        self.assertEqual(
            self.engine.evaluate(
                self.rule,
                track_id="person-1",
                centroid=(0.7, 0.7),
                timestamp=0,
            ),
            RuleDecision.PENDING,
        )
        self.assertEqual(
            self.engine.evaluate(
                self.rule,
                track_id="person-1",
                centroid=(0.7, 0.7),
                timestamp=3,
            ),
            RuleDecision.TRIGGERED,
        )

    def test_exit_clears_pending_state(self):
        self.engine.evaluate(
            self.rule,
            track_id="person-1",
            centroid=(0.7, 0.7),
            timestamp=0,
        )
        self.assertEqual(
            self.engine.evaluate(
                self.rule,
                track_id="person-1",
                centroid=(0.2, 0.2),
                timestamp=1,
            ),
            RuleDecision.CLEAR,
        )
        self.assertEqual(
            self.engine.evaluate(
                self.rule,
                track_id="person-1",
                centroid=(0.7, 0.7),
                timestamp=2,
            ),
            RuleDecision.PENDING,
        )


if __name__ == "__main__":
    unittest.main()
