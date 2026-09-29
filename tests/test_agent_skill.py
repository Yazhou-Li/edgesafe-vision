import json
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL_DIR = ROOT / ".agents" / "skills" / "edge-ai-deployment-doctor"
SKILL_FILE = SKILL_DIR / "SKILL.md"
ASSET_FILE = SKILL_DIR / "assets" / "check-plan.example.json"


class AgentSkillTests(unittest.TestCase):
    def test_skill_manifest_is_well_formed(self):
        text = SKILL_FILE.read_text(encoding="utf-8")
        self.assertTrue(text.startswith("---\n"))

        parts = text.split("---", 2)
        self.assertEqual(len(parts), 3)
        frontmatter = parts[1]

        name_match = re.search(r"^name:\s*([^\n]+)$", frontmatter, re.MULTILINE)
        description_match = re.search(
            r"^description:\s*([^\n]+)$",
            frontmatter,
            re.MULTILINE,
        )

        self.assertIsNotNone(name_match)
        self.assertIsNotNone(description_match)

        name = name_match.group(1).strip()
        description = description_match.group(1).strip()

        self.assertEqual(name, SKILL_DIR.name)
        self.assertRegex(name, r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
        self.assertLessEqual(len(name), 64)
        self.assertTrue(description)
        self.assertLessEqual(len(description), 1024)

    def test_skill_bundles_reference_and_synthetic_asset(self):
        self.assertTrue(
            (SKILL_DIR / "references" / "triage-playbook.md").is_file()
        )

        payload = json.loads(ASSET_FILE.read_text(encoding="utf-8"))
        self.assertEqual(
            set(payload),
            {"http", "tcp", "files"},
        )
        self.assertTrue(
            all("127.0.0.1" in value for value in payload["http"])
        )
        self.assertTrue(
            all(value.startswith("127.0.0.1:") for value in payload["tcp"])
        )


if __name__ == "__main__":
    unittest.main()
