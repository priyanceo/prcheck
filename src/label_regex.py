"""Label regex filter: restrict labels to those whose names match a pattern."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class RegexRule:
    """A compiled regex rule applied to a candidate label name."""

    pattern: str
    compiled: re.Pattern = field(init=False, repr=False)

    def __post_init__(self) -> None:
        if not self.pattern or not self.pattern.strip():
            raise ValueError("RegexRule pattern must not be blank")
        self.compiled = re.compile(self.pattern)

    def matches(self, label: str) -> bool:
        """Return True if *label* fully matches the pattern."""
        return bool(self.compiled.fullmatch(label))


@dataclass
class RegexResult:
    """Outcome of applying the regex filter to a single label."""

    label: str
    allowed: bool
    matched_pattern: Optional[str]

    def to_dict(self) -> dict:
        return {
            "label": self.label,
            "allowed": self.allowed,
            "matched_pattern": self.matched_pattern,
        }


class LabelRegexFilter:
    """Decides whether a label is allowed based on a list of regex rules.

    If no rules are configured every label is allowed.
    """

    def __init__(self, rules: List[RegexRule]) -> None:
        self._rules = rules

    def check(self, label: str) -> RegexResult:
        """Return a RegexResult for *label*."""
        if not self._rules:
            return RegexResult(label=label, allowed=True, matched_pattern=None)
        for rule in self._rules:
            if rule.matches(label):
                return RegexResult(label=label, allowed=True, matched_pattern=rule.pattern)
        return RegexResult(label=label, allowed=False, matched_pattern=None)

    def filter_labels(self, labels: List[str]) -> List[str]:
        """Return only the labels that pass the regex filter."""
        return [lbl for lbl in labels if self.check(lbl).allowed]
