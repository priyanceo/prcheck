"""Dry-run support: collect planned label changes without applying them."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List


@dataclass
class PlannedChange:
    """A single label action that would be applied in a real run."""

    pr_number: int
    repo: str
    action: str          # 'add' | 'remove' | 'skip'
    label: str
    reason: str = ""

    def to_dict(self) -> dict:
        return {
            "pr_number": self.pr_number,
            "repo": self.repo,
            "action": self.action,
            "label": self.label,
            "reason": self.reason,
        }


@dataclass
class DryRunReport:
    """Accumulates all planned changes for a dry run."""

    pr_number: int
    repo: str
    changes: List[PlannedChange] = field(default_factory=list)

    def record(self, action: str, label: str, reason: str = "") -> None:
        self.changes.append(
            PlannedChange(
                pr_number=self.pr_number,
                repo=self.repo,
                action=action,
                label=label,
                reason=reason,
            )
        )

    def has_changes(self) -> bool:
        return len(self.changes) > 0

    def to_dict(self) -> dict:
        return {
            "pr_number": self.pr_number,
            "repo": self.repo,
            "changes": [c.to_dict() for c in self.changes],
        }

    def format_summary(self) -> str:
        if not self.has_changes():
            return f"[dry-run] PR #{self.pr_number}: no label changes planned."
        lines = [f"[dry-run] PR #{self.pr_number} planned changes:"]
        for c in self.changes:
            reason_part = f" ({c.reason})" if c.reason else ""
            lines.append(f"  {c.action.upper():6s}  {c.label}{reason_part}")
        return "\n".join(lines)
