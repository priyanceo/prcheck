"""Label inheritance: when a label is applied, automatically apply its parent labels."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Set


@dataclass
class InheritanceRule:
    label: str
    inherits_from: List[str]

    def __post_init__(self) -> None:
        self.label = self.label.strip()
        if not self.label:
            raise ValueError("InheritanceRule.label must not be blank")
        self.inherits_from = [p.strip() for p in self.inherits_from]
        if not self.inherits_from:
            raise ValueError("InheritanceRule.inherits_from must not be empty")
        blanks = [p for p in self.inherits_from if not p]
        if blanks:
            raise ValueError("InheritanceRule.inherits_from entries must not be blank")

    def to_dict(self) -> dict:
        return {"label": self.label, "inherits_from": list(self.inherits_from)}


@dataclass
class InheritanceResult:
    label: str
    added_parents: List[str] = field(default_factory=list)
    already_present: List[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "label": self.label,
            "added_parents": list(self.added_parents),
            "already_present": list(self.already_present),
        }


class LabelInheritanceResolver:
    def __init__(self, rules: List[InheritanceRule]) -> None:
        self._map: Dict[str, List[str]] = {}
        for rule in rules:
            self._map[rule.label.lower()] = [p.lower() for p in rule.inherits_from]

    def resolve(self, label: str, current_labels: Set[str]) -> InheritanceResult:
        """Return parents that should be added when *label* is applied."""
        key = label.strip().lower()
        parents = self._map.get(key, [])
        result = InheritanceResult(label=label)
        for parent in parents:
            if parent in {l.lower() for l in current_labels}:
                result.already_present.append(parent)
            else:
                result.added_parents.append(parent)
        return result

    def resolve_all(self, labels: Set[str]) -> Dict[str, InheritanceResult]:
        """Resolve inheritance for every label in *labels*."""
        return {label: self.resolve(label, labels) for label in labels}
