"""Label weight assignment and ranking."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class WeightRule:
    label: str
    weight: float = 1.0

    def __post_init__(self) -> None:
        self.label = self.label.strip()
        if not self.label:
            raise ValueError("label must not be blank")
        if self.weight < 0:
            raise ValueError("weight must be non-negative")

    def to_dict(self) -> Dict[str, object]:
        return {"label": self.label, "weight": self.weight}


@dataclass
class WeightResult:
    label: str
    weight: float
    reason: str = ""

    def to_dict(self) -> Dict[str, object]:
        return {"label": self.label, "weight": self.weight, "reason": self.reason}


@dataclass
class LabelWeightResolver:
    _rules: Dict[str, WeightRule] = field(default_factory=dict)
    default_weight: float = 1.0

    def add_rule(self, rule: WeightRule) -> None:
        self._rules[rule.label.lower()] = rule

    def resolve(self, label: str) -> WeightResult:
        key = label.strip().lower()
        rule = self._rules.get(key)
        if rule is not None:
            return WeightResult(
                label=label,
                weight=rule.weight,
                reason=f"matched weight rule for '{rule.label}'",
            )
        return WeightResult(
            label=label,
            weight=self.default_weight,
            reason="default weight applied",
        )

    def rank(self, labels: List[str]) -> List[WeightResult]:
        results = [self.resolve(lbl) for lbl in labels]
        results.sort(key=lambda r: r.weight, reverse=True)
        return results

    def labels(self) -> List[str]:
        return [r.label for r in self._rules.values()]
