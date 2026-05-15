"""Parse the *label_regex* section of the prcheck config."""

from __future__ import annotations

from typing import Any, Dict

from src.label_regex import LabelRegexFilter, RegexRule


def parse_regex_config(config: Dict[str, Any]) -> LabelRegexFilter:
    """Build a :class:`LabelRegexFilter` from the top-level config dict.

    Expected YAML shape::

        label_regex:
          patterns:
            - "^(bug|feature|chore)(/.+)?$"
            - "^size/.*"

    Returns a filter with no rules (allow-all) when the section is absent
    or malformed.
    """
    section = config.get("label_regex")
    if not isinstance(section, dict):
        return LabelRegexFilter(rules=[])

    raw_patterns = section.get("patterns")
    if not isinstance(raw_patterns, list):
        return LabelRegexFilter(rules=[])

    rules: list[RegexRule] = []
    for entry in raw_patterns:
        if not isinstance(entry, str) or not entry.strip():
            continue
        try:
            rules.append(RegexRule(pattern=entry.strip()))
        except Exception:
            # Skip patterns that fail to compile
            continue

    return LabelRegexFilter(rules=rules)
