"""Parse staleness configuration from the prcheck YAML config."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict

_DEFAULT_STALE_DAYS = 30


@dataclass
class StalenessConfig:
    enabled: bool = True
    default_stale_after_days: int = _DEFAULT_STALE_DAYS
    per_label_days: Dict[str, int] = field(default_factory=dict)

    def stale_days_for(self, label: str) -> int:
        return self.per_label_days.get(label, self.default_stale_after_days)


def parse_staleness_config(config: dict) -> StalenessConfig:
    """Extract staleness settings from the top-level config dict."""
    section = config.get("staleness")
    if not isinstance(section, dict):
        return StalenessConfig()

    enabled = bool(section.get("enabled", True))
    default_days = int(section.get("stale_after_days", _DEFAULT_STALE_DAYS))

    per_label_days: Dict[str, int] = {}
    raw_per_label = section.get("per_label", {})
    if isinstance(raw_per_label, dict):
        for label, days in raw_per_label.items():
            if isinstance(label, str) and isinstance(days, int) and days > 0:
                per_label_days[label] = days

    return StalenessConfig(
        enabled=enabled,
        default_stale_after_days=default_days,
        per_label_days=per_label_days,
    )
