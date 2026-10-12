"""Explicit acceptance-profile parsing for reusable EdgeSafe Doctor check plans."""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path

from .doctor import DoctorConfig, parse_target


@dataclass(frozen=True)
class AcceptanceProfile:
    name: str
    proves: tuple[str, ...]
    does_not_prove: tuple[str, ...]
    checks: dict[str, tuple[str, ...]]


_ALLOWED_CHECKS = {"http", "tcp", "files"}


def load_acceptance_profile(path: str) -> AcceptanceProfile:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("profile root must be a JSON object")
    if set(data) != {"name", "proves", "doesNotProve", "checks"}:
        raise ValueError("profile must contain name, proves, doesNotProve, and checks")
    if not isinstance(data["name"], str) or not data["name"].strip():
        raise ValueError("profile name must be a non-empty string")
    for key in ("proves", "doesNotProve"):
        if not isinstance(data[key], list) or not all(isinstance(x, str) for x in data[key]):
            raise ValueError(f"{key} must be an array of strings")
    checks = data["checks"]
    if not isinstance(checks, dict) or set(checks) - _ALLOWED_CHECKS:
        raise ValueError("checks may contain only http, tcp, and files")
    normalized = {}
    for key, values in checks.items():
        if not isinstance(values, list) or not all(isinstance(x, str) for x in values):
            raise ValueError(f"checks.{key} must be an array of strings")
        normalized[key] = tuple(values)
    return AcceptanceProfile(
        name=data["name"],
        proves=tuple(data["proves"]),
        does_not_prove=tuple(data["doesNotProve"]),
        checks=normalized,
    )


def profile_to_doctor_config(
    profile: AcceptanceProfile,
    *,
    profile_path: str,
) -> DoctorConfig:
    """Translate a loaded profile into the existing DoctorConfig contract.

    Relative file checks are resolved from the directory containing the profile,
    so the same profile behaves consistently from any working directory.
    """
    base = Path(profile_path).expanduser().resolve().parent
    file_paths = tuple(
        str(path if path.is_absolute() else (base / path).resolve())
        for raw_path in profile.checks.get("files", ())
        for path in (Path(raw_path).expanduser(),)
    )

    tcp_targets = []
    for value in profile.checks.get("tcp", ()):
        try:
            tcp_targets.append(parse_target(value))
        except argparse.ArgumentTypeError as exc:
            raise ValueError(f"invalid profile tcp target {value!r}: {exc}") from exc

    return DoctorConfig(
        http_urls=profile.checks.get("http", ()),
        tcp_targets=tuple(tcp_targets),
        file_paths=file_paths,
    )
