"""Parse deprecation configuration into a LabelDeprecationChecker."""
from __future__ import annotations

from typing import Any, Dict

from src.label_deprecation import DeprecationRule, LabelDeprecationChecker


def parse_deprecation_config(config: Dict[str, Any]) -> LabelDeprecationChecker:
    """Build a LabelDeprecationChecker from the top-level config dict.

    Expected config shape::

        deprecation:
          labels:
            - label: old-label
              reason: "Use new-label instead"
              replacement: new-label
            - label: legacy
              reason: "No longer used"
    """
    checker = LabelDeprecationChecker()

    section = config.get("deprecation")
    if not isinstance(section, dict):
        return checker

    entries = section.get("labels")
    if not isinstance(entries, list):
        return checker

    for entry in entries:
        if not isinstance(entry, dict):
            continue
        label = entry.get("label", "")
        if not isinstance(label, str) or not label.strip():
            continue
        reason = entry.get("reason", "")
        if not isinstance(reason, str):
            reason = ""
        replacement = entry.get("replacement")
        if not isinstance(replacement, str):
            replacement = None
        try:
            rule = DeprecationRule(
                label=label,
                reason=reason,
                replacement=replacement,
            )
            checker.add_rule(rule)
        except ValueError:
            continue

    return checker
