import unittest

from edgesafe.alarms import Alarm, AlarmState


class AlarmLifecycleTests(unittest.TestCase):
    def test_open_ack_resolve(self):
        alarm = Alarm(
            alarm_id="A-DEMO-1",
            rule_id="demo-overcrowd",
            camera_id="CAM-DEMO-01",
            opened_at=10,
        )
        self.assertEqual(alarm.state, AlarmState.OPEN)

        alarm.acknowledge(12)
        self.assertEqual(alarm.state, AlarmState.ACKNOWLEDGED)

        alarm.resolve(20)
        self.assertEqual(alarm.state, AlarmState.RESOLVED)

    def test_resolved_alarm_cannot_be_acknowledged(self):
        alarm = Alarm("A-1", "R-1", "CAM-1", 0)
        alarm.resolve(1)
        with self.assertRaises(ValueError):
            alarm.acknowledge(2)


if __name__ == "__main__":
    unittest.main()
