"""Label priority resolution: when multiple rules match, apply ordering rules."""
from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class PriorityRule:
    label: str
    priority: int = 0  # higher value = higher priority

    def __post_init__(self) -> None:
        if not isinstance(self.label, str) or not self.label.strip():
            raise ValueError("PriorityRule.label must be a non-empty string")
        if not isinstance(self.priority, int):
            raise ValueError("PriorityRule.priority must be an integer")


@dataclass
class PriorityResult:
    ordered: List[str]
    dropped: List[str]

    def to_dict(self) -> dict:
        return {"ordered": list(self.ordered), "dropped": list(self.dropped)}


class LabelPriorityResolver:
    """Sort and optionally cap labels according to priority rules."""

    def __init__(self, rules: List[PriorityRule], max_labels: Optional[int] = None) -> None:
        self._rules = {r.label: r.priority for r in rules}
        self._max_labels = max_labels

    def resolve(self, labels: List[str]) -> PriorityResult:
        """Return labels sorted by priority (desc). Drop extras if max_labels set."""
        sorted_labels = sorted(
            labels,
            key=lambda lbl: self._rules.get(lbl, 0),
            reverse=True,
        )
        if self._max_labels is not None and self._max_labels >= 0:
            ordered = sorted_labels[: self._max_labels]
            dropped = sorted_labels[self._max_labels :]
        else:
            ordered = sorted_labels
            dropped = []
        return PriorityResult(ordered=ordered, dropped=dropped)
