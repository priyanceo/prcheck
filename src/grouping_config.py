"""Parse label grouping configuration from the prcheck config dict."""
from __future__ import annotations

from typing import Any, Dict

from src.label_grouping import GroupingRule, LabelGroupingResolver


def parse_grouping_config(config: Dict[str, Any]) -> LabelGroupingResolver:
    """Parse the ``grouping`` section and return a :class:`LabelGroupingResolver`.

    Expected YAML shape::

        grouping:
          - group: "ci"
            members: ["ci/build", "ci/test"]
          - group: "docs"
            members: ["documentation", "readme"]
    """
    resolver = LabelGroupingResolver()
    section = config.get("grouping")
    if not isinstance(section, list):
        return resolver

    for entry in section:
        if not isinstance(entry, dict):
            continue
        group = entry.get("group", "")
        members = entry.get("members", [])
        if not isinstance(members, list) or not members:
            continue
        try:
            rule = GroupingRule(group=str(group), members=frozenset(str(m) for m in members))
            resolver.add_rule(rule)
        except (ValueError, TypeError):
            continue

    return resolver
