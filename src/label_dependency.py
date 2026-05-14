"""Label dependency enforcement: ensure required labels are present before others."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set


@dataclass
class DependencyRule:
    label: str
    requires: List[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        if not self.label or not self.label.strip():
            raise ValueError("DependencyRule.label must not be blank")
        if not self.requires:
            raise ValueError("DependencyRule.requires must contain at least one label")

    def missing_deps(self, present: Set[str]) -> List[str]:
        """Return required labels that are absent from *present*."""
        return [r for r in self.requires if r not in present]


@dataclass
class DependencyResult:
    label: str
    allowed: bool
    missing: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict:
        return {
            "label": self.label,
            "allowed": self.allowed,
            "missing": list(self.missing),
        }


class LabelDependencyEnforcer:
    """Check whether labels satisfy their declared dependencies."""

    def __init__(self, rules: Optional[List[DependencyRule]] = None) -> None:
        self._rules: Dict[str, DependencyRule] = {}
        for rule in rules or []:
            self._rules[rule.label] = rule

    def check(self, label: str, present: Set[str]) -> DependencyResult:
        """Return a DependencyResult for *label* given the *present* label set."""
        rule = self._rules.get(label)
        if rule is None:
            return DependencyResult(label=label, allowed=True, missing=[])
        missing = rule.missing_deps(present)
        return DependencyResult(label=label, allowed=len(missing) == 0, missing=missing)

    def check_all(self, candidates: Set[str], present: Set[str]) -> List[DependencyResult]:
        """Check every candidate label and return results for those with rules."""
        results: List[DependencyResult] = []
        for label in sorted(candidates):
            result = self.check(label, present)
            if label in self._rules:
                results.append(result)
        return results
