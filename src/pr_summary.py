"""Builds a human-readable summary of labelling actions taken on a PR."""

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class PRSummary:
    pr_number: int
    repo: str
    labels_added: List[str] = field(default_factory=list)
    labels_removed: List[str] = field(default_factory=list)
    labels_skipped: List[str] = field(default_factory=list)
    total_changes: int = 0
    matched_rules: List[str] = field(default_factory=list)

    def add_label(self, label: str) -> None:
        if label not in self.labels_added:
            self.labels_added.append(label)

    def remove_label(self, label: str) -> None:
        if label not in self.labels_removed:
            self.labels_removed.append(label)

    def skip_label(self, label: str) -> None:
        if label not in self.labels_skipped:
            self.labels_skipped.append(label)

    def add_matched_rule(self, rule_name: str) -> None:
        if rule_name not in self.matched_rules:
            self.matched_rules.append(rule_name)

    def to_dict(self) -> dict:
        return {
            "pr_number": self.pr_number,
            "repo": self.repo,
            "labels_added": self.labels_added,
            "labels_removed": self.labels_removed,
            "labels_skipped": self.labels_skipped,
            "total_changes": self.total_changes,
            "matched_rules": self.matched_rules,
        }

    def format_summary(self) -> str:
        lines = [
            f"PR #{self.pr_number} — {self.repo}",
            f"  Total changes : {self.total_changes}",
        ]
        if self.labels_added:
            lines.append(f"  Added         : {', '.join(self.labels_added)}")
        if self.labels_removed:
            lines.append(f"  Removed       : {', '.join(self.labels_removed)}")
        if self.labels_skipped:
            lines.append(f"  Skipped       : {', '.join(self.labels_skipped)}")
        if self.matched_rules:
            lines.append(f"  Matched rules : {', '.join(self.matched_rules)}")
        if not self.labels_added and not self.labels_removed:
            lines.append("  No label changes made.")
        return "\n".join(lines)
