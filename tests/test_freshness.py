import unittest

from edgesafe.freshness import FreshnessMonitor, FreshnessPolicy


class FreshnessMonitorTests(unittest.TestCase):
    def setUp(self):
        self.monitor = FreshnessMonitor(
            FreshnessPolicy(
                video_stale_after=5,
                metadata_stale_after=2,
                max_skew_seconds=1,
            )
        )

    def test_fresh_and_aligned(self):
        self.monitor.mark_video("CAM-1", 10.0)
        self.monitor.mark_metadata("CAM-1", 10.4)
        report = self.monitor.report("CAM-1", 11.0)
        self.assertTrue(report.healthy)

    def test_stale_video_is_not_healthy(self):
        self.monitor.mark_video("CAM-1", 1.0)
        self.monitor.mark_metadata("CAM-1", 9.5)
        report = self.monitor.report("CAM-1", 10.0)
        self.assertFalse(report.video_fresh)
        self.assertFalse(report.healthy)

    def test_temporal_skew_is_detected(self):
        self.monitor.mark_video("CAM-1", 10.0)
        self.monitor.mark_metadata("CAM-1", 12.0)
        report = self.monitor.report("CAM-1", 12.1)
        self.assertFalse(report.aligned)


if __name__ == "__main__":
    unittest.main()
