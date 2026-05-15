"""Parse label weight configuration."""
from __future__ import annotations

from typing import Any, Dict

from src.label_weight import LabelWeightResolver, WeightRule

_DEFAULT_WEIGHT = 1.0


def parse_weight_config(config: Dict[str, Any]) -> LabelWeightResolver:
    """Build a LabelWeightResolver from the top-level config dict.

    Expected config shape::

        weights:
          default: 1.0
          labels:
            - label: bug
              weight: 3.0
            - label: documentation
              weight: 0.5
    """
    section = config.get("weights")
    if not isinstance(section, dict):
        return LabelWeightResolver(default_weight=_DEFAULT_WEIGHT)

    default_weight = section.get("default", _DEFAULT_WEIGHT)
    if not isinstance(default_weight, (int, float)) or default_weight < 0:
        default_weight = _DEFAULT_WEIGHT

    resolver = LabelWeightResolver(default_weight=float(default_weight))

    labels_raw = section.get("labels")
    if not isinstance(labels_raw, list):
        return resolver

    for entry in labels_raw:
        if not isinstance(entry, dict):
            continue
        label = entry.get("label", "")
        weight = entry.get("weight", _DEFAULT_WEIGHT)
        if not isinstance(label, str) or not label.strip():
            continue
        if not isinstance(weight, (int, float)) or weight < 0:
            continue
        try:
            resolver.add_rule(WeightRule(label=label, weight=float(weight)))
        except ValueError:
            continue

    return resolver
