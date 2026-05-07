"""Parse throttle configuration from the prcheck YAML config dict."""
from __future__ import annotations

from typing import Any, Dict

from src.label_throttle import ThrottleConfig

_DEFAULT_WINDOW = 3600
_DEFAULT_MAX_OPS = 5


def parse_throttle_config(config: Dict[str, Any]) -> ThrottleConfig:
    """Extract throttle settings from the top-level config mapping.

    Expected YAML shape::

        throttle:
          window_seconds: 3600
          max_operations: 5

    Missing keys fall back to defaults.
    """
    section = config.get("throttle", {})
    if not isinstance(section, dict):
        section = {}

    window = section.get("window_seconds", _DEFAULT_WINDOW)
    max_ops = section.get("max_operations", _DEFAULT_MAX_OPS)

    if not isinstance(window, int) or window <= 0:
        window = _DEFAULT_WINDOW
    if not isinstance(max_ops, int) or max_ops <= 0:
        max_ops = _DEFAULT_MAX_OPS

    return ThrottleConfig(window_seconds=window, max_operations=max_ops)
