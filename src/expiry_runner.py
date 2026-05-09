"""Expiry runner: remove labels from PRs whose TTL has elapsed."""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import List

from src.expiry_config import LabelExpiryConfig
from src.github_client import GitHubClient
from src.label_expiry import ExpiryRecord, LabelExpiryStore

logger = logging.getLogger(__name__)


@dataclass
class ExpiryRunResult:
    removed: List[ExpiryRecord] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)

    @property
    def success(self) -> bool:
        return len(self.errors) == 0

    def to_dict(self) -> dict:
        return {
            "removed": [r.to_dict() for r in self.removed],
            "errors": self.errors,
        }


def run_expiry(
    pr_number: int,
    repo: str,
    client: GitHubClient,
    store: LabelExpiryStore,
    config: LabelExpiryConfig,
    dry_run: bool = False,
) -> ExpiryRunResult:
    """Check for expired labels on *pr_number* and remove them via *client*.

    If *dry_run* is ``True`` the GitHub API is not called but removals are
    still logged and returned in the result.
    """
    result = ExpiryRunResult()
    expired = store.expired_for_pr(pr_number)

    for record in expired:
        label = record.label
        if config.ttl_for(label) is None:
            logger.debug("Skipping %s — no TTL configured (may have been removed from config)", label)
            continue

        if dry_run:
            logger.info("[dry-run] Would remove expired label '%s' from PR #%d", label, pr_number)
            result.removed.append(record)
            continue

        try:
            client.remove_label(repo=repo, pr_number=pr_number, label=label)
            store.remove(label, pr_number)
            result.removed.append(record)
            logger.info("Removed expired label '%s' from PR #%d", label, pr_number)
        except Exception as exc:  # noqa: BLE001
            msg = f"Failed to remove label '{label}' from PR #{pr_number}: {exc}"
            logger.error(msg)
            result.errors.append(msg)

    return result
