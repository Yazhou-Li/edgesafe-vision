import json
import tempfile
import unittest
from pathlib import Path

from edgesafe.doctor import run_checks
from edgesafe.profiles import (
    load_acceptance_profile,
    profile_to_doctor_config,
)


class AcceptanceProfileTests(unittest.TestCase):
    def test_loads_explicit_profile(self):
        profile = load_acceptance_profile("examples/profiles/local-service-readiness.json")
        self.assertEqual(profile.name, "local-service-readiness")
        self.assertIn("http", profile.checks)
        self.assertTrue(profile.does_not_prove)

    def test_loaded_profile_runs_through_doctor_config(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            fixtures = root / "fixtures"
            profiles = root / "profiles"
            fixtures.mkdir()
            profiles.mkdir()
            ready = fixtures / "ready.txt"
            ready.write_text("ok", encoding="utf-8")
            profile_path = profiles / "local-files.json"
            profile_path.write_text(
                json.dumps(
                    {
                        "name": "local-files",
                        "proves": ["The local synthetic fixture is readable."],
                        "doesNotProve": ["Any remote service is healthy."],
                        "checks": {"files": ["../fixtures/ready.txt"]},
                    }
                ),
                encoding="utf-8",
            )

            profile = load_acceptance_profile(str(profile_path))
            config = profile_to_doctor_config(
                profile,
                profile_path=str(profile_path),
            )
            results = run_checks(
                http_urls=config.http_urls,
                tcp_targets=config.tcp_targets,
                file_paths=config.file_paths,
            )

        self.assertEqual(config.file_paths, (str(ready.resolve()),))
        file_result = next(item for item in results if item.name.startswith("file:"))
        self.assertEqual(file_result.status, "PASS")

    def test_rejects_hidden_or_unknown_check_types(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "bad.json"
            path.write_text(
                '{"name":"bad","proves":[],"doesNotProve":[],"checks":{"magic":["x"]}}',
                encoding="utf-8",
            )
            with self.assertRaises(ValueError):
                load_acceptance_profile(str(path))


if __name__ == "__main__":
    unittest.main()
