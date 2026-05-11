"""Parses scorer configuration from the loaded YAML config dict."""
from __future__ import annotations

from typing import Any, Dict

_DEFAULT_THRESHOLD = 0.0
_DEFAULT_RULE_WEIGHT = 1.0


def parse_scorer_config(config: Dict[str, Any]) -> dict:
    """Extract scorer settings from the top-level config dict.

    Expected YAML shape::

        scorer:
          threshold: 0.25        # minimum confidence to apply a label
          default_rule_weight: 2.0

    Returns a plain dict with keys ``threshold`` and ``default_rule_weight``.
    """
    section = config.get("scorer", {})
    if not isinstance(section, dict):
        section = {}

    raw_threshold = section.get("threshold", _DEFAULT_THRESHOLD)
    try:
        threshold = float(raw_threshold)
    except (TypeError, ValueError):
        threshold = _DEFAULT_THRESHOLD
    threshold = max(0.0, min(1.0, threshold))

    raw_weight = section.get("default_rule_weight", _DEFAULT_RULE_WEIGHT)
    try:
        default_rule_weight = float(raw_weight)
    except (TypeError, ValueError):
        default_rule_weight = _DEFAULT_RULE_WEIGHT
    if default_rule_weight <= 0:
        default_rule_weight = _DEFAULT_RULE_WEIGHT

    return {
        "threshold": threshold,
        "default_rule_weight": default_rule_weight,
    }
