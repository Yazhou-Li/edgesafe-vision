"""End-to-end synthetic EdgeSafe Vision pipeline demo.

This demo requires no camera, GPU, MQTT broker, or production credentials.
It composes the public normalized-event adapter, occupancy rule engine, and
alarm lifecycle using a deterministic JSONL fixture.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from edgesafe import Alarm, AlarmState, OccupancyRule, OccupancyRuleEngine
from edgesafe.adapters import parse_normalized_mqtt_event
from edgesafe.rules import RuleDecision


DEFAULT_INPUT = Path(__file__).with_name("pipeline_events.jsonl")


def load_payloads(path: Path) -> list[dict]:
    payloads: list[dict] = []
    for line_number, raw in enumerate(
        path.read_text(encoding="utf-8").splitlines(),
        start=1,
    ):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        try:
            value = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ValueError(
                f"invalid JSON on line {line_number}: {exc.msg}"
            ) from exc
        if not isinstance(value, dict):
            raise ValueError(f"line {line_number} must contain a JSON object")
        payloads.append(value)
    return payloads


def run_demo(path: Path) -> list[dict]:
    rule = OccupancyRule(
        rule_id="demo-overcrowding",
        camera_id="CAM-DEMO-01",
        threshold=4,
        duration_seconds=3,
        cooldown_seconds=5,
    )
    engine = OccupancyRuleEngine()

    active_alarm: Alarm | None = None
    alarm_sequence = 0
    trace: list[dict] = []

    print("EdgeSafe Vision synthetic pipeline")
    print("event -> normalized EdgeEvent -> occupancy rule -> alarm lifecycle")
    print()

    for payload in load_payloads(path):
        event = parse_normalized_mqtt_event("edgesafe/events", payload)

        if event.camera_id != rule.camera_id:
            raise ValueError(
                f"unexpected camera {event.camera_id!r}; "
                f"expected {rule.camera_id!r}"
            )

        count = event.attributes.get("personCount")
        if isinstance(count, bool) or not isinstance(count, int) or count < 0:
            raise ValueError("personCount must be a non-negative integer")

        decision = engine.evaluate(
            rule,
            person_count=count,
            timestamp=event.observed_at,
        )

        action = "none"
        if decision == RuleDecision.TRIGGERED:
            alarm_sequence += 1
            active_alarm = Alarm(
                alarm_id=f"DEMO-ALARM-{alarm_sequence:02d}",
                rule_id=rule.rule_id,
                camera_id=rule.camera_id,
                opened_at=event.observed_at,
            )
            action = "alarm_opened"
        elif (
            decision == RuleDecision.CLEAR
            and active_alarm is not None
            and active_alarm.state != AlarmState.RESOLVED
        ):
            active_alarm.resolve(event.observed_at)
            action = "alarm_resolved"

        alarm_state = (
            "none"
            if active_alarm is None
            else active_alarm.state.value
        )

        step = {
            "eventId": event.event_id,
            "timestamp": event.observed_at,
            "personCount": count,
            "decision": decision.value,
            "action": action,
            "alarmState": alarm_state,
        }
        trace.append(step)

        print(
            f"t={event.observed_at:>4.0f}s  "
            f"count={count:<2d}  "
            f"decision={decision.value:<9}  "
            f"action={action:<14}  "
            f"alarm={alarm_state}"
        )

    opened = sum(1 for step in trace if step["action"] == "alarm_opened")
    resolved = sum(1 for step in trace if step["action"] == "alarm_resolved")

    print()
    print(
        f"SUMMARY events={len(trace)} "
        f"alarms_opened={opened} alarms_resolved={resolved}"
    )

    return trace


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run the deterministic EdgeSafe Vision pipeline demo."
    )
    parser.add_argument(
        "--input",
        type=Path,
        default=DEFAULT_INPUT,
        help="JSONL normalized-event fixture.",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    run_demo(args.input)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
