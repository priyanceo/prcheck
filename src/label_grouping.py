"""Label grouping: cluster related labels under named groups."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, FrozenSet, List, Optional


@dataclass
class GroupingRule:
    group: str
    members: FrozenSet[str]

    def __post_init__(self) -> None:
        if not self.group or not self.group.strip():
            raise ValueError("group name must not be blank")
        if not self.members:
            raise ValueError("members must not be empty")
        object.__setattr__(self, "group", self.group.strip())
        object.__setattr__(
            self, "members", frozenset(m.strip().lower() for m in self.members)
        )

    def contains(self, label: str) -> bool:
        return label.strip().lower() in self.members

    def to_dict(self) -> dict:
        return {"group": self.group, "members": sorted(self.members)}


@dataclass
class GroupingResult:
    label: str
    group: Optional[str]
    matched: bool

    def to_dict(self) -> dict:
        return {"label": self.label, "group": self.group, "matched": self.matched}


@dataclass
class LabelGroupingResolver:
    _rules: List[GroupingRule] = field(default_factory=list)

    def add_rule(self, rule: GroupingRule) -> None:
        self._rules.append(rule)

    def resolve(self, label: str) -> GroupingResult:
        for rule in self._rules:
            if rule.contains(label):
                return GroupingResult(label=label, group=rule.group, matched=True)
        return GroupingResult(label=label, group=None, matched=False)

    def groups_for_labels(self, labels: List[str]) -> Dict[str, List[str]]:
        """Return a mapping of group -> [labels] for the given label list."""
        result: Dict[str, List[str]] = {}
        for label in labels:
            r = self.resolve(label)
            if r.matched and r.group:
                result.setdefault(r.group, []).append(label)
        return result
