"""Entry-point logic: wire config, GitHub client and labeler together."""

from __future__ import annotations

import os
from typing import List

from .config import load_config
from .github_client import GitHubClient, PullRequestFile, client_from_env
from .labeler import Labeler


def _total_changes(files: List[PullRequestFile]) -> int:
    return sum(f.changes for f in files)


def run(
    config_path: str,
    pr_number: int,
    client: GitHubClient | None = None,
) -> List[str]:
    """Compute and apply labels for *pr_number*.

    Returns the list of labels that were applied.
    """
    if client is None:
        client = client_from_env()

    config = load_config(config_path)
    labeler = Labeler(
        path_rules=config["path_rules"],
        size_rules=config["size_rules"],
    )

    pr_files = client.get_pr_files(pr_number)
    changed_paths = [f.filename for f in pr_files]
    diff_size = _total_changes(pr_files)

    labels = labeler.compute_labels(changed_paths, diff_size)

    if labels:
        client.set_labels(pr_number, labels)
        print(f"Applied labels {labels} to PR #{pr_number}")
    else:
        print(f"No labels matched for PR #{pr_number}")

    return labels


def main() -> None:  # pragma: no cover
    """CLI entry-point used by the GitHub Action step."""
    config_path = os.environ.get("INPUT_CONFIG", ".github/prcheck.yml")
    pr_number_raw = os.environ.get("INPUT_PR_NUMBER") or os.environ.get("PR_NUMBER")
    if not pr_number_raw:
        raise SystemExit("PR number not provided (INPUT_PR_NUMBER or PR_NUMBER).")
    run(config_path=config_path, pr_number=int(pr_number_raw))


if __name__ == "__main__":  # pragma: no cover
    main()
