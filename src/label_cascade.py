"""Label cascade: automatically apply secondary labels when a primary label is applied."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Set


@dataclass
class CascadeRule:
    trigger: str
    cascades: List[str]

    def __post_init__(self) -> None:
        self.trigger = self.trigger.strip().lower()
        if not self.trigger:
            raise ValueError("CascadeRule trigger must not be blank")
        self.cascades = [c.strip().lower() for c in self.cascades]
        if not self.cascades:
            raise ValueError("CascadeRule cascades must not be empty")
        blanks = [c for c in self.cascades if not c]
        if blanks:
            raise ValueError("CascadeRule cascades must not contain blank labels")

    def to_dict(self) -> Dict:
        return {"trigger": self.trigger, "cascades": list(self.cascades)}


@dataclass
class CascadeResult:
    trigger: str
    applied: List[str] = field(default_factory=list)
    skipped: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict:
        return {
            "trigger": self.trigger,
            "applied": list(self.applied),
            "skipped": list(self.skipped),
        }


class LabelCascadeResolver:
    def __init__(self, rules: List[CascadeRule]) -> None:
        self._rules: Dict[str, List[str]] = {}
        for rule in rules:
            self._rules.setdefault(rule.trigger, []).extend(rule.cascades)

    def resolve(self, active_labels: Set[str]) -> List[CascadeResult]:
        """Return cascade results for each triggered label."""
        results: List[CascadeResult] = []
        for trigger, cascades in self._rules.items():
            if trigger not in active_labels:
                continue
            result = CascadeResult(trigger=trigger)
            for label in cascades:
                if label in active_labels:
                    result.skipped.append(label)
                else:
                    result.applied.append(label)
            results.append(result)
        return results

    def all_cascaded(self, active_labels: Set[str]) -> Set[str]:
        """Return the full set of labels that should be added via cascade."""
        new_labels: Set[str] = set()
        for result in self.resolve(active_labels):
            new_labels.update(result.applied)
        return new_labels
