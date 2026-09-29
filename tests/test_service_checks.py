import subprocess
import unittest
from unittest.mock import patch

from edgesafe.service_checks import check_service


class ServiceCheckTests(unittest.TestCase):
    @patch("edgesafe.service_checks._run")
    def test_linux_active_and_inactive(self, run):
        run.return_value = subprocess.CompletedProcess([], 0, "active\n", "")
        self.assertEqual(check_service("demo.service", system="Linux").status, "PASS")
        run.assert_called_with(["systemctl", "is-active", "demo.service"])

        run.return_value = subprocess.CompletedProcess([], 3, "inactive\n", "")
        result = check_service("demo.service", system="Linux")
        self.assertEqual(result.status, "FAIL")
        self.assertIn("inactive", result.detail)

    @patch("edgesafe.service_checks._run")
    def test_windows_uses_argument_list_and_reports_state(self, run):
        run.return_value = subprocess.CompletedProcess([], 0, "Ready\n", "")
        result = check_service("EdgeSafe Demo", system="Windows")
        self.assertEqual(result.status, "PASS")
        args = run.call_args.args[0]
        self.assertEqual(args[-1], "EdgeSafe Demo")
        self.assertIn("-NonInteractive", args)

    def test_unsupported_platform_warns(self):
        result = check_service("demo", system="Darwin")
        self.assertEqual(result.status, "WARN")
        self.assertIn("unsupported", result.detail)

    @patch("edgesafe.service_checks._run", side_effect=FileNotFoundError())
    def test_missing_platform_tool_warns(self, run):
        self.assertEqual(check_service("demo", system="Linux").status, "WARN")

    def test_rejects_multiline_target(self):
        with self.assertRaises(ValueError):
            check_service("demo\nother", system="Linux")


if __name__ == "__main__":
    unittest.main()
