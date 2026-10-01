"""Explicit acceptance-profile parsing for reusable EdgeSafe Doctor check plans."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path


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
