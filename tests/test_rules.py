import unittest

from edgesafe.rules import OccupancyRule, OccupancyRuleEngine, RuleDecision


class OccupancyRuleEngineTests(unittest.TestCase):
    def setUp(self):
        self.engine = OccupancyRuleEngine()
        self.rule = OccupancyRule(
            rule_id="demo-overcrowd",
            camera_id="CAM-DEMO-01",
            threshold=4,
            duration_seconds=3,
            cooldown_seconds=10,
        )

    def test_below_threshold_is_clear(self):
        result = self.engine.evaluate(
            self.rule, person_count=3, timestamp=0
        )
        self.assertEqual(result, RuleDecision.CLEAR)

    def test_threshold_requires_persistence(self):
        first = self.engine.evaluate(
            self.rule, person_count=4, timestamp=0
        )
        second = self.engine.evaluate(
            self.rule, person_count=4, timestamp=2.9
        )
        third = self.engine.evaluate(
            self.rule, person_count=4, timestamp=3.0
        )

        self.assertEqual(first, RuleDecision.PENDING)
        self.assertEqual(second, RuleDecision.PENDING)
        self.assertEqual(third, RuleDecision.TRIGGERED)

    def test_clearing_resets_pending_window(self):
        self.engine.evaluate(self.rule, person_count=4, timestamp=0)
        self.assertEqual(
            self.engine.evaluate(self.rule, person_count=2, timestamp=1),
            RuleDecision.CLEAR,
        )
        self.assertEqual(
            self.engine.evaluate(self.rule, person_count=4, timestamp=2),
            RuleDecision.PENDING,
        )

    def test_cooldown_prevents_repeat_alarm(self):
        self.engine.evaluate(self.rule, person_count=4, timestamp=0)
        self.engine.evaluate(self.rule, person_count=4, timestamp=3)

        result = self.engine.evaluate(
            self.rule, person_count=4, timestamp=5
        )
        self.assertEqual(result, RuleDecision.COOLDOWN)


if __name__ == "__main__":
    unittest.main()
