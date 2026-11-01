import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from edgesafe.doctor import (
    _safe_url_label,
    baseline_results,
    build_evidence_bundle,
    check_file,
    check_http,
    load_check_config,
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

    def test_malformed_http_urls_never_echo_credentials(self):
        malformed = (
            "https://demo:synthetic-secret@example.test:invalid/health?token=synthetic-secret",
            "https://demo:synthetic-secret@[broken/health?token=synthetic-secret",
        )
        for url in malformed:
            with self.subTest(url_type="malformed"):
                self.assertEqual(_safe_url_label(url), "<invalid-url>")
                result = check_http(url)
                self.assertEqual(result.status, "FAIL")
                self.assertEqual(result.name, "<invalid-url>")
                self.assertNotIn("synthetic-secret", str(result))
                self.assertNotIn("example.test", str(result))

    @patch("edgesafe.doctor.urllib.request.urlopen")
    def test_http_exception_message_is_not_copied_to_evidence(self, urlopen):
        urlopen.side_effect = RuntimeError("synthetic-secret from HTTP client")
        result = check_http(
            "https://demo:synthetic-secret@example.test/health?token=synthetic-secret"
        )
        self.assertEqual(result.status, "FAIL")
        self.assertEqual(result.name, "https://example.test/health")
        self.assertIn("RuntimeError", result.detail)
        self.assertNotIn("synthetic-secret", str(result))
        urlopen.assert_called_once()

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


if __name__ == "__main__":
    unittest.main()
