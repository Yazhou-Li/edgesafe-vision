import unittest

from edgesafe.camera_health import CameraHealthState, evaluate_camera_health
from edgesafe.freshness import FreshnessMonitor, FreshnessPolicy


class CameraHealthTests(unittest.TestCase):
    def setUp(self):
        self.monitor = FreshnessMonitor(
            FreshnessPolicy(
                video_stale_after=5,
                metadata_stale_after=2,
                max_skew_seconds=1,
            )
        )

    def test_disabled_wins_over_missing_stream(self):
        report = self.monitor.report("CAM-1", 10)
        health = evaluate_camera_health(report, stream_available=False, enabled=False)
        self.assertEqual(health.state, CameraHealthState.DISABLED)

    def test_stream_state_unknown_is_unknown(self):
        report = self.monitor.report("CAM-1", 10)
        health = evaluate_camera_health(report, stream_available=None)
        self.assertEqual(health.state, CameraHealthState.UNKNOWN)

    def test_unavailable_stream_is_offline(self):
        report = self.monitor.report("CAM-1", 10)
        health = evaluate_camera_health(report, stream_available=False)
        self.assertEqual(health.state, CameraHealthState.OFFLINE)

    def test_fresh_signals_are_healthy_then_stale_is_degraded(self):
        self.monitor.mark_video("CAM-1", 10)
        self.monitor.mark_metadata("CAM-1", 10.4)
        fresh = evaluate_camera_health(
            self.monitor.report("CAM-1", 11),
            stream_available=True,
        )
        stale = evaluate_camera_health(
            self.monitor.report("CAM-1", 20),
            stream_available=True,
        )
        self.assertEqual(fresh.state, CameraHealthState.HEALTHY)
        self.assertEqual(stale.state, CameraHealthState.DEGRADED)

    def test_recovery_after_new_observations(self):
        self.monitor.mark_video("CAM-1", 1)
        self.monitor.mark_metadata("CAM-1", 1)
        self.assertEqual(
            evaluate_camera_health(
                self.monitor.report("CAM-1", 10),
                stream_available=True,
            ).state,
            CameraHealthState.DEGRADED,
        )
        self.monitor.mark_video("CAM-1", 10)
        self.monitor.mark_metadata("CAM-1", 10)
        self.assertEqual(
            evaluate_camera_health(
                self.monitor.report("CAM-1", 10.5),
                stream_available=True,
            ).state,
            CameraHealthState.HEALTHY,
        )


if __name__ == "__main__":
    unittest.main()
