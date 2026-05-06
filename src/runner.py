"""Orchestrates label evaluation and application (or dry-run simulation)."""
from __future__ import annotations

import os
from typing import List

from src.github_client import GitHubClient, PullRequestFile
from src.labeler import LabelRule, SizeRule
from src.pr_summary import PRSummary
from src.dry_run import DryRunReport
from src.dry_run_formatter import write_dry_run_summary


def _total_changes(files: List[PullRequestFile]) -> int:
    return sum(f.changes for f in files)


def run(
    client: GitHubClient,
    repo: str,
    pr_number: int,
    label_rules: List[LabelRule],
    size_rules: List[SizeRule],
    dry_run: bool = False,
) -> PRSummary:
    files = client.get_pr_files(repo, pr_number)
    changed_paths = [f.filename for f in files]
    total = _total_changes(files)

    summary = PRSummary(pr_number=pr_number, repo=repo)
    dry_report = DryRunReport(pr_number=pr_number, repo=repo) if dry_run else None

    labels_to_add: list[str] = []

    for rule in label_rules:
        if rule.matches(changed_paths):
            labels_to_add.append(rule.label)
            summary.add_matched_rule(str(rule))

    for rule in size_rules:
        if rule.matches(total):
            labels_to_add.append(rule.label)
            summary.add_matched_rule(str(rule))

    existing = set(client.get_pr_labels(repo, pr_number))

    for label in labels_to_add:
        if label in existing:
            summary.skip_label(label)
            if dry_report:
                dry_report.record("skip", label, "already applied")
        else:
            summary.add_label(label)
            if dry_report:
                dry_report.record("add", label, "rule matched")
            elif not dry_run:
                client.add_label(repo, pr_number, label)

    if dry_report:
        write_dry_run_summary(dry_report)
        print(dry_report.format_summary())

    return summary


def main() -> None:  # pragma: no cover
    token = os.environ["GITHUB_TOKEN"]
    repo = os.environ["GITHUB_REPOSITORY"]
    pr_number = int(os.environ["PR_NUMBER"])
    dry_run = os.environ.get("DRY_RUN", "false").lower() == "true"

    from src.config import load_config
    from src.github_client import GitHubClient

    cfg = load_config(os.environ.get("CONFIG_PATH", ".github/prcheck.yml"))
    client = GitHubClient(token=token)
    run(
        client=client,
        repo=repo,
        pr_number=pr_number,
        label_rules=cfg.get("label_rules", []),
        size_rules=cfg.get("size_rules", []),
        dry_run=dry_run,
    )
