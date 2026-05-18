"""Parse cascade configuration from the prcheck YAML config dict."""
from __future__ import annotations

from typing import Any, Dict, List

from src.label_cascade import CascadeRule, LabelCascadeResolver


def parse_cascade_config(config: Dict[str, Any]) -> LabelCascadeResolver:
    """Build a LabelCascadeResolver from the top-level config dict.

    Expected shape::

        cascade:
          - trigger: "backend"
            cascades:
              - "needs-review"
              - "python"
    """
    section = config.get("cascade")
    if not isinstance(section, list):
        return LabelCascadeResolver([])

    rules: List[CascadeRule] = []
    for entry in section:
        if not isinstance(entry, dict):
            continue
        trigger = entry.get("trigger", "")
        cascades = entry.get("cascades", [])
        if not isinstance(trigger, str) or not trigger.strip():
            continue
        if not isinstance(cascades, list) or not cascades:
            continue
        cascade_labels = [c for c in cascades if isinstance(c, str) and c.strip()]
        if not cascade_labels:
            continue
        try:
            rules.append(CascadeRule(trigger=trigger, cascades=cascade_labels))
        except ValueError:
            continue

    return LabelCascadeResolver(rules)
