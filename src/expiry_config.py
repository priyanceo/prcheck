"""Parse label-expiry configuration from the action YAML config."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List


@dataclass
class LabelExpiryConfig:
    """Holds per-label TTL values (in seconds)."""
    ttl_by_label: Dict[str, float] = field(default_factory=dict)

    def ttl_for(self, label: str) -> float | None:
        """Return TTL seconds for *label*, or None if no expiry is configured."""
        return self.ttl_by_label.get(label)


def parse_expiry_config(config: Dict[str, Any]) -> LabelExpiryConfig:
    """Build a :class:`LabelExpiryConfig` from the top-level config mapping.

    Expected shape (all optional)::

        expiry:
          labels:
            - label: stale
              ttl_days: 7
            - label: needs-review
              ttl_hours: 48
    """
    section = config.get("expiry", {})
    if not isinstance(section, dict):
        return LabelExpiryConfig()

    entries: List[Dict[str, Any]] = section.get("labels", [])
    if not isinstance(entries, list):
        return LabelExpiryConfig()

    ttl_by_label: Dict[str, float] = {}
    for entry in entries:
        if not isinstance(entry, dict):
            continue
        label = entry.get("label", "")
        if not isinstance(label, str) or not label.strip():
            continue
        ttl: float = 0.0
        if "ttl_seconds" in entry:
            ttl = float(entry["ttl_seconds"])
        elif "ttl_hours" in entry:
            ttl = float(entry["ttl_hours"]) * 3600
        elif "ttl_days" in entry:
            ttl = float(entry["ttl_days"]) * 86400
        if ttl > 0:
            ttl_by_label[label.strip()] = ttl

    return LabelExpiryConfig(ttl_by_label=ttl_by_label)
