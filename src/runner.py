"""Orchestrates PR label evaluation and applies labels via the GitHub API."""

from __future__ import annotations

import os
from typing import List

from src.audit_log import AuditEntry, AuditLog
from src.config import load_config
from src.config_validator import validate_config
from src.github_client import GitHubClient, PullRequestFile
from src.labeler import LabelRule, SizeRule
from src.metrics import RunMetrics


def _total_changes(files: List[PullRequestFile]) -> int:
    return sum(f.changes for f in files)


def run(
    *,
    token: str,
    repo: str,
    pr_number: int,
    config_path: str,
    audit_log: AuditLog | None = None,
) -> RunMetrics:
    metrics = RunMetrics(pr_number=pr_number, repo=repo)

    raw = load_config(config_path)
    validate_config(raw)

    path_rules: List[LabelRule] = [
        LabelRule(label=r["label"], patterns=r["patterns"])
        for r in raw.get("path_rules", [])
    ]
    size_rules: List[SizeRule] = [
        SizeRule(label=r["label"], min_changes=r.get("min", 0), max_changes=r.get("max"))
        for r in raw.get("size_rules", [])
    ]

    client = GitHubClient(token=token, repo=repo)
    files = client.get_pr_files(pr_number)
    total = _total_changes(files)
    changed_paths = [f.filename for f in files]

    desired: set[str] = set()
    for rule in path_rules:
        if rule.matches(changed_paths):
            desired.add(rule.label)
    for rule in size_rules:
        if rule.matches(total):
            desired.add(rule.label)

    current = set(client.get_pr_labels(pr_number))
    to_add = sorted(desired - current)
    to_remove = sorted(current - desired)

    for label in to_add:
        client.add_label(pr_number, label)
    for label in to_remove:
        client.remove_label(pr_number, label)

    if audit_log is not None:
        audit_log.record(
            AuditEntry(
                pr_number=pr_number,
                repo=repo,
                labels_added=to_add,
                labels_removed=to_remove,
                triggered_by=os.environ.get("GITHUB_ACTOR"),
            )
        )

    metrics.finish(labels_added=to_add, labels_removed=to_remove, files_changed=len(files))
    return metrics


def main() -> None:  # pragma: no cover
    token = os.environ["GITHUB_TOKEN"]
    repo = os.environ["GITHUB_REPOSITORY"]
    pr_number = int(os.environ["PR_NUMBER"])
    config_path = os.environ.get("CONFIG_PATH", ".github/prcheck.yml")
    log_path = os.environ.get("AUDIT_LOG_PATH", "logs/audit.log")

    audit_log = AuditLog(log_path)
    metrics = run(
        token=token,
        repo=repo,
        pr_number=pr_number,
        config_path=config_path,
        audit_log=audit_log,
    )
    print(metrics.format_summary())


if __name__ == "__main__":
    main()
