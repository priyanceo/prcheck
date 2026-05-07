"""Parse label priority configuration from the YAML config dict."""
from typing import Any, Dict, List, Optional

from src.label_priority import LabelPriorityResolver, PriorityRule


def parse_priority_config(
    config: Dict[str, Any]
) -> LabelPriorityResolver:
    """Build a LabelPriorityResolver from the top-level config dict.

    Expected shape (all keys optional)::

        label_priority:
          max_labels: 3          # optional int
          rules:
            - label: bug
              priority: 10
            - label: enhancement
              priority: 5
    """
    section: Dict[str, Any] = config.get("label_priority") or {}

    max_labels: Optional[int] = section.get("max_labels")  # type: ignore[assignment]
    if max_labels is not None:
        max_labels = int(max_labels)

    raw_rules: List[Any] = section.get("rules") or []
    rules: List[PriorityRule] = []
    for entry in raw_rules:
        label = str(entry.get("label", "")).strip()
        priority = int(entry.get("priority", 0))
        if label:
            rules.append(PriorityRule(label=label, priority=priority))

    return LabelPriorityResolver(rules=rules, max_labels=max_labels)
