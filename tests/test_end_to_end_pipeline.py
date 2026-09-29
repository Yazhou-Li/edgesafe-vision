import json
import unittest
from pathlib import Path

from edgesafe import Alarm, AlarmState, OccupancyRule, OccupancyRuleEngine
from edgesafe.adapters import parse_normalized_mqtt_event
from edgesafe.rules import RuleDecision


class EndToEndPipelineTests(unittest.TestCase):
    def test_synthetic_fixture_drives_alarm_lifecycle(self):
        fixture = (
            Path(__file__).resolve().parents[1]
            / "examples"
            / "pipeline_events.jsonl"
        )

        rule = OccupancyRule(
            rule_id="demo-overcrowding",
            camera_id="CAM-DEMO-01",
            threshold=4,
            duration_seconds=3,
            cooldown_seconds=5,
        )
        engine = OccupancyRuleEngine()

        alarm = None
        decisions = []
        actions = []

        for raw in fixture.read_text(encoding="utf-8").splitlines():
            if not raw.strip():
                continue
            payload = json.loads(raw)
            event = parse_normalized_mqtt_event(
                "edgesafe/events",
                payload,
            )
            count = event.attributes["personCount"]

            decision = engine.evaluate(
                rule,
                person_count=count,
                timestamp=event.observed_at,
            )
            decisions.append(decision)

            action = "none"
            if decision == RuleDecision.TRIGGERED:
                alarm = Alarm(
                    alarm_id=f"A-{event.event_id}",
                    rule_id=rule.rule_id,
                    camera_id=rule.camera_id,
                    opened_at=event.observed_at,
                )
                action = "alarm_opened"
            elif (
                decision == RuleDecision.CLEAR
                and alarm is not None
                and alarm.state != AlarmState.RESOLVED
            ):
                alarm.resolve(event.observed_at)
                action = "alarm_resolved"

            actions.append(action)

        self.assertEqual(
            decisions,
            [
                RuleDecision.CLEAR,
                RuleDecision.PENDING,
                RuleDecision.PENDING,
                RuleDecision.TRIGGERED,
                RuleDecision.COOLDOWN,
                RuleDecision.CLEAR,
                RuleDecision.PENDING,
                RuleDecision.TRIGGERED,
            ],
        )
        self.assertEqual(actions.count("alarm_opened"), 2)
        self.assertEqual(actions.count("alarm_resolved"), 1)


if __name__ == "__main__":
    unittest.main()
