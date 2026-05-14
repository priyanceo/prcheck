"""Detect and report stale labels on pull requests."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import List, Optional


@dataclass
class StaleLabelEntry:
    label: str
    applied_at: datetime
    stale_after_days: int

    @property
    def is_stale(self) -> bool:
        age = (datetime.now(timezone.utc) - self.applied_at).days
        return age >= self.stale_after_days

    def to_dict(self) -> dict:
        return {
            "label": self.label,
            "applied_at": self.applied_at.isoformat(),
            "stale_after_days": self.stale_after_days,
            "is_stale": self.is_stale,
        }


@dataclass
class StalenessReport:
    pr_number: int
    repo: str
    stale: List[StaleLabelEntry] = field(default_factory=list)
    fresh: List[StaleLabelEntry] = field(default_factory=list)

    def record(self, entry: StaleLabelEntry) -> None:
        if entry.is_stale:
            self.stale.append(entry)
        else:
            self.fresh.append(entry)

    @property
    def has_stale(self) -> bool:
        return len(self.stale) > 0

    def to_dict(self) -> dict:
        return {
            "pr_number": self.pr_number,
            "repo": self.repo,
            "stale": [e.to_dict() for e in self.stale],
            "fresh": [e.to_dict() for e in self.fresh],
        }


def build_staleness_report(
    pr_number: int,
    repo: str,
    applied_labels: List[dict],
    stale_after_days: int = 30,
) -> StalenessReport:
    """Build a staleness report from a list of applied label dicts.

    Each dict must have 'label' and 'applied_at' (ISO-8601 string) keys.
    """
    report = StalenessReport(pr_number=pr_number, repo=repo)
    for item in applied_labels:
        applied_at = datetime.fromisoformat(item["applied_at"])
        if applied_at.tzinfo is None:
            applied_at = applied_at.replace(tzinfo=timezone.utc)
        entry = StaleLabelEntry(
            label=item["label"],
            applied_at=applied_at,
            stale_after_days=item.get("stale_after_days", stale_after_days),
        )
        report.record(entry)
    return report
