"""Label exclusion: prevent specific labels from being applied under defined conditions."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import FrozenSet, List, Set


@dataclass(frozen=True)
class ExclusionRule:
    """A rule that blocks a label when any of the excluded_when labels are present."""

    label: str
    excluded_when: FrozenSet[str]

    def __post_init__(self) -> None:
        if not self.label or not self.label.strip():
            raise ValueError("ExclusionRule.label must not be blank")
        if not self.excluded_when:
            raise ValueError("ExclusionRule.excluded_when must not be empty")

    def is_excluded(self, present_labels: Set[str]) -> bool:
        """Return True if any exclusion trigger label is in present_labels."""
        return bool(self.excluded_when & present_labels)


@dataclass
class ExclusionResult:
    label: str
    allowed: bool
    blocked_by: List[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "label": self.label,
            "allowed": self.allowed,
            "blocked_by": list(self.blocked_by),
        }


class LabelExclusionEnforcer:
    """Checks a set of candidate labels against exclusion rules."""

    def __init__(self, rules: List[ExclusionRule]) -> None:
        self._rules: dict[str, ExclusionRule] = {r.label: r for r in rules}

    def check(self, label: str, present_labels: Set[str]) -> ExclusionResult:
        """Return an ExclusionResult for *label* given the currently present labels."""
        rule = self._rules.get(label)
        if rule is None:
            return ExclusionResult(label=label, allowed=True)

        blocked_by = sorted(rule.excluded_when & present_labels)
        if blocked_by:
            return ExclusionResult(label=label, allowed=False, blocked_by=blocked_by)
        return ExclusionResult(label=label, allowed=True)

    def filter_labels(
        self, candidates: List[str], present_labels: Set[str]
    ) -> List[str]:
        """Return only the candidates that are not excluded."""
        return [
            lbl
            for lbl in candidates
            if self.check(lbl, present_labels).allowed
        ]
