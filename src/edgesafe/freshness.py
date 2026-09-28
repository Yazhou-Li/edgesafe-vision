"""Freshness monitoring for live video and AI metadata.

A production system can have a healthy HTTP endpoint while still showing stale
video frames or outdated AI overlays. This module tracks the two signals
independently so deployments can detect temporal drift instead of treating
"200 OK" as proof of real-time behavior.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Optional


@dataclass(frozen=True)
class FreshnessPolicy:
    video_stale_after: float = 5.0
    metadata_stale_after: float = 2.0
    max_skew_seconds: float = 1.0

    def __post_init__(self) -> None:
        if self.video_stale_after <= 0:
            raise ValueError("video_stale_after must be > 0")
        if self.metadata_stale_after <= 0:
            raise ValueError("metadata_stale_after must be > 0")
        if self.max_skew_seconds < 0:
            raise ValueError("max_skew_seconds must be >= 0")


@dataclass
class CameraFreshness:
    last_video_at: Optional[float] = None
    last_metadata_at: Optional[float] = None


@dataclass(frozen=True)
class FreshnessReport:
    camera_id: str
    video_fresh: bool
    metadata_fresh: bool
    aligned: bool
    video_age: Optional[float]
    metadata_age: Optional[float]
    skew_seconds: Optional[float]

    @property
    def healthy(self) -> bool:
        return self.video_fresh and self.metadata_fresh and self.aligned


class FreshnessMonitor:
    def __init__(self, policy: FreshnessPolicy | None = None) -> None:
        self.policy = policy or FreshnessPolicy()
        self._state: Dict[str, CameraFreshness] = {}

    def mark_video(self, camera_id: str, timestamp: float) -> None:
        self._state.setdefault(camera_id, CameraFreshness()).last_video_at = timestamp

    def mark_metadata(self, camera_id: str, timestamp: float) -> None:
        self._state.setdefault(camera_id, CameraFreshness()).last_metadata_at = timestamp

    def report(self, camera_id: str, now: float) -> FreshnessReport:
        state = self._state.get(camera_id, CameraFreshness())

        video_age = None if state.last_video_at is None else now - state.last_video_at
        metadata_age = (
            None if state.last_metadata_at is None else now - state.last_metadata_at
        )

        video_fresh = (
            video_age is not None
            and 0 <= video_age <= self.policy.video_stale_after
        )
        metadata_fresh = (
            metadata_age is not None
            and 0 <= metadata_age <= self.policy.metadata_stale_after
        )

        if state.last_video_at is None or state.last_metadata_at is None:
            skew = None
            aligned = False
        else:
            skew = abs(state.last_video_at - state.last_metadata_at)
            aligned = skew <= self.policy.max_skew_seconds

        return FreshnessReport(
            camera_id=camera_id,
            video_fresh=video_fresh,
            metadata_fresh=metadata_fresh,
            aligned=aligned,
            video_age=video_age,
            metadata_age=metadata_age,
            skew_seconds=skew,
        )
