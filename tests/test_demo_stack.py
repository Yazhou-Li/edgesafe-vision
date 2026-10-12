import shutil
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
COMPOSE_FILE = ROOT / "demo-stack" / "compose.yaml"
EXPECTED_SUMMARY = "SUMMARY events=8 alarms_opened=2 alarms_resolved=1"


def _docker_compose_available() -> bool:
    if shutil.which("docker") is None:
        return False
    try:
        compose = subprocess.run(
            ["docker", "compose", "version"],
            capture_output=True,
            text=True,
            timeout=15,
            check=False,
        )
        daemon = subprocess.run(
            ["docker", "info"],
            capture_output=True,
            text=True,
            timeout=15,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired):
        return False
    return compose.returncode == 0 and daemon.returncode == 0


class DemoStackTests(unittest.TestCase):
    def test_stack_is_optional_local_and_has_safe_cleanup(self):
        compose = COMPOSE_FILE.read_text(encoding="utf-8")
        docs = (ROOT / "demo-stack" / "README.md").read_text(encoding="utf-8")
        broker_config = (
            ROOT / "demo-stack" / "mosquitto-no-auth.conf"
        ).read_text(encoding="utf-8")
        pyproject = (ROOT / "pyproject.toml").read_text(encoding="utf-8")

        self.assertIn("./mosquitto-no-auth.conf", compose)
        self.assertIn("/mosquitto/config/mosquitto.conf", compose)
        self.assertIn("allow_anonymous true", broker_config)
        self.assertIn("listener 1883 0.0.0.0", broker_config)
        self.assertIn("127.0.0.1", compose)
        self.assertIn('restart: "no"', compose)
        self.assertIn("--remove-orphans", docs)
        self.assertIn(EXPECTED_SUMMARY, docs)
        self.assertNotIn("docker", pyproject.lower())

    @unittest.skipUnless(
        _docker_compose_available(),
        "Docker daemon with Compose is required for the integration smoke test",
    )
    def test_compose_stack_smoke(self):
        up = subprocess.run(
            [
                "docker",
                "compose",
                "-f",
                str(COMPOSE_FILE),
                "up",
                "--build",
                "--abort-on-container-exit",
                "--exit-code-from",
                "edgesafe-demo",
            ],
            cwd=ROOT,
            capture_output=True,
            text=True,
            timeout=180,
            check=False,
        )
        output = f"{up.stdout}\n{up.stderr}"
        try:
            self.assertEqual(up.returncode, 0, output)
            self.assertIn(EXPECTED_SUMMARY, output)
        finally:
            subprocess.run(
                [
                    "docker",
                    "compose",
                    "-f",
                    str(COMPOSE_FILE),
                    "down",
                    "--volumes",
                    "--remove-orphans",
                ],
                cwd=ROOT,
                capture_output=True,
                text=True,
                timeout=60,
                check=False,
            )


if __name__ == "__main__":
    unittest.main()
