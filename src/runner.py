"""Orchestrate label evaluation and apply changes via the GitHub API."""
from __future__ import annotations

import logging
from typing import List

from src.config import load_config
from src.config_validator import validate_config
from src.github_client import GitHubClient, PullRequestFile
from src.labeler import LabelRule, SizeRule
from src.metrics import RunMetrics, format_summary
from src.metrics_reporter import MetricsReporter

logger = logging.getLogger(__name__)


def _total_changes(files: List[PullRequestFile]) -> int:
    return sum(f.changes for f in files)


def run(
    *,
    config_path: str,
    token: str,
    repo: str,
    pr_number: int,
    reporter: MetricsReporter | None = None,
) -> None:
    """Load config, evaluate rules, and update PR labels."""
    metrics = RunMetrics(pr_number=pr_number)

    raw = load_config(config_path)
    validate_config(raw)

    client = GitHubClient(token=token, repo=repo)
    files = client.get_pr_files(pr_number)
    current_labels = client.get_pr_labels(pr_number)

    metrics.files_evaluated = len(files)
    metrics.total_changes = _total_changes(files)

    path_rules: List[LabelRule] = raw.get("path_rules", [])
    size_rules: List[SizeRule] = raw.get("size_rules", [])

    desired: set[str] = set()
    file_paths = [f.filename for f in files]

    for rule in path_rules:
        if rule.matches(file_paths):
            desired.add(rule.label)

    for rule in size_rules:
        if rule.matches(metrics.total_changes):
            desired.add(rule.label)

    current: set[str] = set(current_labels)
    to_add = sorted(desired - current)
    to_remove = sorted(current - desired)

    for label in to_add:
        client.add_label(pr_number, label)
    for label in to_remove:
        client.remove_label(pr_number, label)

    metrics.labels_added = to_add
    metrics.labels_removed = to_remove
    metrics.finish()

    logger.info(format_summary(metrics))

    if reporter is not None:
        reporter.record(metrics)


def main() -> None:
    import os

    logging.basicConfig(level=logging.INFO)
    run(
        config_path=os.environ["PRCHECK_CONFIG"],
        token=os.environ["GITHUB_TOKEN"],
        repo=os.environ["GITHUB_REPOSITORY"],
        pr_number=int(os.environ["PR_NUMBER"]),
        reporter=MetricsReporter(),
    )


if __name__ == "__main__":
    main()
