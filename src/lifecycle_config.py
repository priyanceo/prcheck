"""Parse lifecycle configuration from the top-level config dict."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict


@dataclass
class LifecycleConfig:
    """Controls which lifecycle events are tracked and whether reporting is enabled."""
    track_created: bool = True
    track_updated: bool = True
    track_removed: bool = True
    report_enabled: bool = True
    tracked_labels: list = field(default_factory=list)  # empty = all labels

    def should_track(self, label: str, event: str) -> bool:
        if self.tracked_labels and label not in self.tracked_labels:
            return False
        return {
            "created": self.track_created,
            "updated": self.track_updated,
            "removed": self.track_removed,
        }.get(event, False)


def parse_lifecycle_config(config: dict) -> LifecycleConfig:
    """Build a LifecycleConfig from the raw YAML-parsed config dict."""
    if not isinstance(config, dict):
        return LifecycleConfig()

    section = config.get("lifecycle")
    if not isinstance(section, dict):
        return LifecycleConfig()

    def _bool(key: str, default: bool) -> bool:
        val = section.get(key, default)
        return bool(val) if isinstance(val, bool) else default

    raw_labels = section.get("tracked_labels", [])
    tracked = (
        [str(l).strip() for l in raw_labels if str(l).strip()]
        if isinstance(raw_labels, list)
        else []
    )

    return LifecycleConfig(
        track_created=_bool("track_created", True),
        track_updated=_bool("track_updated", True),
        track_removed=_bool("track_removed", True),
        report_enabled=_bool("report_enabled", True),
        tracked_labels=tracked,
    )
