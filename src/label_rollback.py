"""Label rollback: revert labels applied in a previous run using audit log history."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

from src.audit_log import AuditLog


@dataclass
class RollbackResult:
    pr_number: int
    repo: str
    removed: List[str] = field(default_factory=list)
    skipped: List[str] = field(default_factory=list)
    error: Optional[str] = None

    @property
    def success(self) -> bool:
        return self.error is None

    def to_dict(self) -> dict:
        return {
            "pr_number": self.pr_number,
            "repo": self.repo,
            "removed": self.removed,
            "skipped": self.skipped,
            "error": self.error,
            "success": self.success,
        }


def run_rollback(
    pr_number: int,
    repo: str,
    audit_log: AuditLog,
    github_client,
    *,
    dry_run: bool = False,
) -> RollbackResult:
    """Remove labels that were added by prcheck in the most recent run for this PR."""
    result = RollbackResult(pr_number=pr_number, repo=repo)

    entries = audit_log.entries_for_pr(pr_number)
    if not entries:
        result.skipped.append("*")
        return result

    # Find the latest run's added labels
    latest = max(entries, key=lambda e: e.timestamp)
    labels_to_remove = [a["label"] for a in latest.actions if a.get("action") == "added"]

    if not labels_to_remove:
        return result

    for label in labels_to_remove:
        try:
            if not dry_run:
                github_client.remove_label(pr_number, label)
            result.removed.append(label)
        except Exception as exc:  # noqa: BLE001
            result.skipped.append(label)
            result.error = str(exc)

    return result
