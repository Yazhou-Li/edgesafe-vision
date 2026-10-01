"""Deterministic camera-health classification composed with freshness evidence."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .freshness import FreshnessReport


class CameraHealthState(str, Enum):
    UNKNOWN = "unknown"
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    OFFLINE = "offline"
    DISABLED = "disabled"


@dataclass(frozen=True)
class CameraHealthReport:
    camera_id: str
    state: CameraHealthState
    reason: str


def evaluate_camera_health(
    freshness: FreshnessReport,
    *,
    stream_available: bool | None,
    enabled: bool = True,
) -> CameraHealthReport:
    """Classify camera health without performing network or device I/O."""
    if not enabled:
        return CameraHealthReport(
            freshness.camera_id,
            CameraHealthState.DISABLED,
            "camera intentionally disabled",
        )
    if stream_available is False:
        return CameraHealthReport(
            freshness.camera_id,
            CameraHealthState.OFFLINE,
            "stream unavailable",
        )
    if stream_available is None:
        return CameraHealthReport(
            freshness.camera_id,
            CameraHealthState.UNKNOWN,
            "stream state unknown",
        )
    if freshness.healthy:
        return CameraHealthReport(
            freshness.camera_id,
            CameraHealthState.HEALTHY,
            "stream available and freshness signals healthy",
        )
    if freshness.last_video_at is None and freshness.last_metadata_at is None:
        return CameraHealthReport(
            freshness.camera_id,
            CameraHealthState.UNKNOWN,
            "no freshness observations yet",
        )
    return CameraHealthReport(
        freshness.camera_id,
        CameraHealthState.DEGRADED,
        "stream available but freshness signals are stale or misaligned",
    )
