"""Parse the 'cooldown' section of the prcheck YAML config."""
from __future__ import annotations

from typing import Any, Dict

from src.label_cooldown import CooldownConfig

_DEFAULT_SECONDS = 0


def parse_cooldown_config(config: Dict[str, Any]) -> CooldownConfig:
    """Return a :class:`CooldownConfig` from the top-level config dict.

    Expected shape::

        cooldown:
          default_seconds: 3600
          labels:
            - label: bug
              seconds: 7200
            - label: wip
              seconds: 1800
    """
    section = config.get("cooldown")
    if not isinstance(section, dict):
        return CooldownConfig()

    default_seconds = section.get("default_seconds", _DEFAULT_SECONDS)
    if not isinstance(default_seconds, int) or default_seconds < 0:
        default_seconds = _DEFAULT_SECONDS

    per_label: dict = {}
    labels_raw = section.get("labels")
    if isinstance(labels_raw, list):
        for entry in labels_raw:
            if not isinstance(entry, dict):
                continue
            label = entry.get("label")
            seconds = entry.get("seconds")
            if not isinstance(label, str) or not label.strip():
                continue
            if not isinstance(seconds, int) or seconds < 0:
                continue
            per_label[label.strip().lower()] = seconds

    return CooldownConfig(default_seconds=default_seconds, per_label=per_label)
