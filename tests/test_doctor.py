import json
from contextlib import redirect_stdout
from io import StringIO
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from edgesafe.doctor import (
    CheckResult,
    _safe_url_label,
    baseline_results,
    build_evidence_bundle,
    check_file,
    load_check_config,
    main,
    parse_target,
    write_evidence_bundle,
)


class DoctorTests(unittest.TestCase):
    def test_parse_target(self):
        self.assertEqual(parse_target("127.0.0.1:5000"), ("127.0.0.1", 5000))

    def test_baseline_has_python_and_disk(self):
        names = {item.name for item in baseline_results()}
        self.assertIn("python", names)
        self.assertIn("disk", names)

    def test_file_check(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "ready.txt"
            path.write_text("ok", encoding="utf-8")

            good = check_file(str(path))
            missing = check_file(str(Path(tmp) / "missing.txt"))

            self.assertEqual(good.status, "PASS")
            self.assertEqual(missing.status, "FAIL")

    def test_url_label_redacts_credentials_and_query(self):
        label = _safe_url_label(
            "https://demo:secret@example.test:8443/health?token=secret#frag"
        )
        self.assertEqual(label, "https://example.test:8443/health")
        self.assertNotIn("secret", label)
        self.assertNotIn("token", label)

    def test_load_check_config(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "doctor.json"
            path.write_text(
                json.dumps(
                    {
                        "http": ["http://127.0.0.1:5000"],
                        "tcp": ["127.0.0.1:1883"],
                        "files": ["./pyproject.toml"],
                    }
                ),
                encoding="utf-8",
            )

            config = load_check_config(str(path))

            self.assertEqual(
                config.http_urls,
                ("http://127.0.0.1:5000",),
            )
            self.assertEqual(
                config.tcp_targets,
                (("127.0.0.1", 1883),),
            )
            self.assertEqual(
                config.file_paths,
                ("./pyproject.toml",),
            )

    def test_unknown_config_key_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "doctor.json"
            path.write_text('{"unknown": []}', encoding="utf-8")

            with self.assertRaises(ValueError):
                load_check_config(str(path))

    def test_evidence_bundle_omits_hostname(self):
        bundle = build_evidence_bundle(baseline_results())

        self.assertEqual(bundle["schema"], "edgesafe-evidence-v1")
        self.assertIn("platform", bundle)
        self.assertIn("checks", bundle)
        self.assertNotIn("hostname", bundle)

    def test_write_evidence_bundle(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "evidence" / "report.json"
            result = write_evidence_bundle(
                str(target),
                baseline_results(),
            )

            self.assertEqual(result, target)
            payload = json.loads(target.read_text(encoding="utf-8"))
            self.assertEqual(payload["schema"], "edgesafe-evidence-v1")

    def test_shareable_evidence_is_opt_in_and_uses_non_reversible_labels(self):
        results = [
            CheckResult("tcp:private.internal:443", "PASS", "connection established"),
            CheckResult("file:/srv/customer/secret.env", "FAIL", "not found"),
        ]
        normal = build_evidence_bundle(results)
        shared = build_evidence_bundle(results, shareable=True)
        shared_again = build_evidence_bundle(results, shareable=True)

        self.assertEqual(normal["checks"][0]["name"], "tcp:private.internal:443")
        self.assertEqual(shared["checks"][0]["status"], "PASS")
        self.assertEqual(shared["checks"][1]["status"], "FAIL")
        self.assertEqual(shared["checks"], shared_again["checks"])
        serialized = json.dumps(shared["checks"])
        self.assertNotIn("private.internal", serialized)
        self.assertNotIn("/srv/customer", serialized)
        self.assertEqual(shared["checks"][0]["name"], "tcp:[redacted-1]")
        self.assertEqual(shared["checks"][1]["name"], "file:[redacted-2]")

    @patch("edgesafe.doctor.run_checks")
    def test_shareable_mode_redacts_json_stdout_and_evidence(self, run_checks):
        run_checks.return_value = [
            CheckResult(
                "tcp:private.internal:443",
                "PASS",
                "connection established",
            ),
            CheckResult(
                "file:/srv/customer/secret.env",
                "FAIL",
                "not found",
            ),
        ]
        with tempfile.TemporaryDirectory() as tmp:
            evidence_path = Path(tmp) / "evidence.json"
            stdout = StringIO()
            with redirect_stdout(stdout):
                code = main(
                    [
                        "--shareable",
                        "--json",
                        "--evidence",
                        str(evidence_path),
                    ]
                )

            json_output = stdout.getvalue()
            evidence = evidence_path.read_text(encoding="utf-8")
            self.assertEqual(code, 1)
            for private_value in ("private.internal", "/srv/customer", "secret.env"):
                self.assertNotIn(private_value, json_output)
                self.assertNotIn(private_value, evidence)
            stdout_checks = json.loads(json_output)
            evidence_checks = json.loads(evidence)["checks"]
            self.assertEqual(stdout_checks, evidence_checks)

    @patch("edgesafe.doctor.run_checks")
    def test_shareable_mode_redacts_printed_evidence_path(self, run_checks):
        run_checks.return_value = [
            CheckResult(
                "http://private.internal/health",
                "PASS",
                "HTTP 200",
            )
        ]
        with tempfile.TemporaryDirectory() as tmp:
            evidence_path = Path(tmp) / "private-customer" / "output.json"
            stdout = StringIO()
            with redirect_stdout(stdout):
                code = main(
                    [
                        "--shareable",
                        "--evidence",
                        str(evidence_path),
                    ]
                )

            output = stdout.getvalue()
            evidence = evidence_path.read_text(encoding="utf-8")

        self.assertEqual(code, 0)
        self.assertIn("EVIDENCE  [redacted path]", output)
        self.assertNotIn(str(evidence_path), output)
        for private_value in ("private-customer", "private.internal"):
            self.assertNotIn(private_value, output)
            self.assertNotIn(private_value, evidence)

    @patch("edgesafe.doctor.run_checks")
    def test_shareable_mode_redacts_terminal_output(self, run_checks):
        run_checks.return_value = [
            CheckResult(
                "http://private.internal/health",
                "PASS",
                "HTTP 200",
            )
        ]
        stdout = StringIO()
        with redirect_stdout(stdout):
            code = main(["--shareable"])

        self.assertEqual(code, 0)
        self.assertIn("http:[redacted-1]", stdout.getvalue())
        self.assertNotIn("private.internal", stdout.getvalue())


if __name__ == "__main__":
    unittest.main()
