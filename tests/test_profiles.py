import tempfile
import unittest
from pathlib import Path

from edgesafe.profiles import load_acceptance_profile


class AcceptanceProfileTests(unittest.TestCase):
    def test_loads_explicit_profile(self):
        profile = load_acceptance_profile("examples/profiles/local-service-readiness.json")
        self.assertEqual(profile.name, "local-service-readiness")
        self.assertIn("http", profile.checks)
        self.assertTrue(profile.does_not_prove)

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
