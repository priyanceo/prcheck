"""Detect and resolve conflicting label assignments."""
from dataclasses import dataclass, field
from typing import Dict, List, Set, Tuple


@dataclass
class ConflictRule:
    """A rule that defines mutually exclusive labels."""
    group: str
    labels: List[str]

    def conflicts_with(self, label_a: str, label_b: str) -> bool:
        """Return True if both labels belong to this exclusive group."""
        return label_a in self.labels and label_b in self.labels


@dataclass
class ConflictResult:
    """Outcome of a conflict check for a set of labels."""
    resolved: List[str] = field(default_factory=list)
    dropped: Dict[str, str] = field(default_factory=dict)  # label -> reason

    def to_dict(self) -> dict:
        return {
            "resolved": self.resolved,
            "dropped": self.dropped,
        }


class LabelConflictResolver:
    """Resolves label conflicts based on configured exclusive groups."""

    def __init__(self, rules: List[ConflictRule]) -> None:
        self._rules = rules

    def resolve(self, labels: List[str]) -> ConflictResult:
        """Given a list of labels, drop conflicting ones (keep first match)."""
        result = ConflictResult()
        seen_groups: Dict[str, str] = {}  # group -> first label that claimed it
        accepted: List[str] = []

        for label in labels:
            conflicting_group = self._find_conflict(label, seen_groups)
            if conflicting_group is not None:
                winner = seen_groups[conflicting_group]
                reason = (
                    f"conflicts with '{winner}' in exclusive group "
                    f"'{conflicting_group}'"
                )
                result.dropped[label] = reason
            else:
                for rule in self._rules:
                    if label in rule.labels:
                        seen_groups[rule.group] = label
                accepted.append(label)

        result.resolved = accepted
        return result

    def _find_conflict(
        self, label: str, seen_groups: Dict[str, str]
    ) -> str | None:
        """Return the group name if this label conflicts with an already-seen label."""
        for rule in self._rules:
            if label in rule.labels and rule.group in seen_groups:
                return rule.group
        return None


def parse_conflict_rules(config: dict) -> List[ConflictRule]:
    """Parse conflict rules from the raw config dict."""
    raw = config.get("label_conflicts", [])
    rules: List[ConflictRule] = []
    for entry in raw:
        group = entry.get("group", "")
        labels = entry.get("labels", [])
        if group and labels:
            rules.append(ConflictRule(group=group, labels=labels))
    return rules
