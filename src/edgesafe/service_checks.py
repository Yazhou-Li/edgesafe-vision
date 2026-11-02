"""Read-only operating-system service state checks."""

from __future__ import annotations

import platform
import subprocess
from dataclasses import dataclass


@dataclass(frozen=True)
class ServiceCheckResult:
    target: str
    status: str
    detail: str


def _run(args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        args,
        capture_output=True,
        text=True,
        timeout=5,
        check=False,
        shell=False,
    )


def check_service(target: str, *, system: str | None = None) -> ServiceCheckResult:
    """Inspect service state without starting, stopping, or mutating it."""
    if not target or any(ch in target for ch in "\r\n\0"):
        raise ValueError("service target must be a non-empty single-line value")

    current = system or platform.system()
    try:
        if current == "Linux":
            result = _run(["systemctl", "is-active", target])
            state = result.stdout.strip() or result.stderr.strip() or "unknown"
            if result.returncode == 0 and state == "active":
                return ServiceCheckResult(target, "PASS", "systemd unit active")
            return ServiceCheckResult(target, "FAIL", f"systemd unit {state}")

        if current == "Windows":
            result = _run(
                [
                    "powershell",
                    "-NoProfile",
                    "-NonInteractive",
                    "-Command",
                    (
                        "param([string]$TaskName) "
                        "(Get-ScheduledTask -TaskName $TaskName -ErrorAction Stop).State"
                    ),
                    "-TaskName",
                    target,
                ]
            )
            state = result.stdout.strip()
            normalized = state.casefold()
            if result.returncode != 0 or not state:
                return ServiceCheckResult(
                    target, "FAIL", "scheduled task not found or unreadable"
                )
            if normalized == "running":
                return ServiceCheckResult(target, "PASS", "scheduled task running")
            if normalized in {"ready", "disabled"}:
                return ServiceCheckResult(
                    target,
                    "WARN",
                    f"scheduled task exists but is {normalized}",
                )
            return ServiceCheckResult(
                target,
                "WARN",
                f"scheduled task state is {state!r}; running status not established",
            )
    except (OSError, subprocess.TimeoutExpired) as exc:
        return ServiceCheckResult(target, "WARN", f"service check unavailable: {type(exc).__name__}")

    return ServiceCheckResult(target, "WARN", f"service checks unsupported on {current}")
