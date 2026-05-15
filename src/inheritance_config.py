"""Parse inheritance configuration from the prcheck YAML config dict."""
from __future__ import annotations

from typing import Any, Dict

from src.label_inheritance import InheritanceRule, LabelInheritanceResolver


def parse_inheritance_config(config: Dict[str, Any]) -> LabelInheritanceResolver:
    """Build a :class:`LabelInheritanceResolver` from the top-level config dict.

    Expected shape::

        inheritance:
          - label: "feature"
            inherits_from:
              - "needs-review"
              - "triage"

    Any malformed entries are silently skipped.
    """
    section = config.get("inheritance")
    if not isinstance(section, list):
        return LabelInheritanceResolver([])

    rules: list[InheritanceRule] = []
    for entry in section:
        if not isinstance(entry, dict):
            continue
        label = entry.get("label", "")
        inherits_from = entry.get("inherits_from", [])
        if not isinstance(label, str) or not isinstance(inherits_from, list):
            continue
        try:
            rules.append(InheritanceRule(label=label, inherits_from=inherits_from))
        except ValueError:
            continue

    return LabelInheritanceResolver(rules)
