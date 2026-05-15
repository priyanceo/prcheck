"""Label deprecation tracking and enforcement."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class DeprecationRule:
    label: str
    reason: str = ""
    replacement: Optional[str] = None

    def __post_init__(self) -> None:
        self.label = self.label.strip()
        if not self.label:
            raise ValueError("DeprecationRule.label must not be blank")
        if self.replacement is not None:
            self.replacement = self.replacement.strip() or None

    def to_dict(self) -> dict:
        return {
            "label": self.label,
            "reason": self.reason,
            "replacement": self.replacement,
        }


@dataclass
class DeprecationResult:
    label: str
    deprecated: bool
    reason: str = ""
    replacement: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "label": self.label,
            "deprecated": self.deprecated,
            "reason": self.reason,
            "replacement": self.replacement,
        }


@dataclass
class LabelDeprecationChecker:
    _rules: Dict[str, DeprecationRule] = field(default_factory=dict)

    def add_rule(self, rule: DeprecationRule) -> None:
        self._rules[rule.label.lower()] = rule

    def check(self, label: str) -> DeprecationResult:
        key = label.strip().lower()
        rule = self._rules.get(key)
        if rule is None:
            return DeprecationResult(label=label, deprecated=False)
        return DeprecationResult(
            label=label,
            deprecated=True,
            reason=rule.reason,
            replacement=rule.replacement,
        )

    def check_all(self, labels: List[str]) -> List[DeprecationResult]:
        return [self.check(lbl) for lbl in labels]

    def deprecated_labels(self) -> List[str]:
        return [r.label for r in self._rules.values()]
