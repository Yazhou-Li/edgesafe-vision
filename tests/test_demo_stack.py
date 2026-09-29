import unittest
from pathlib import Path


class DemoStackTests(unittest.TestCase):
    def test_stack_is_optional_local_and_has_safe_cleanup(self):
        compose = Path("demo-stack/compose.yaml").read_text(encoding="utf-8")
        docs = Path("demo-stack/README.md").read_text(encoding="utf-8")
        pyproject = Path("pyproject.toml").read_text(encoding="utf-8")

        self.assertIn("127.0.0.1", compose)
        self.assertIn('restart: "no"', compose)
        self.assertIn("--remove-orphans", docs)
        self.assertIn("SUMMARY events=8 alarms_opened=2 alarms_resolved=1", docs)
        self.assertNotIn("docker", pyproject.lower())


if __name__ == "__main__":
    unittest.main()
