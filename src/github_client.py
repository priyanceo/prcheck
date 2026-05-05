"""GitHub API client for fetching PR data and applying labels."""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import List

import requests

GITHUB_API_URL = "https://api.github.com"


@dataclass
class PullRequestFile:
    filename: str
    additions: int
    deletions: int

    @property
    def changes(self) -> int:
        return self.additions + self.deletions


class GitHubClient:
    """Thin wrapper around the GitHub REST API."""

    def __init__(self, token: str, repo: str) -> None:
        self.repo = repo
        self._session = requests.Session()
        self._session.headers.update(
            {
                "Authorization": f"Bearer {token}",
                "Accept": "application/vnd.github+json",
                "X-GitHub-Api-Version": "2022-11-28",
            }
        )

    # ------------------------------------------------------------------
    # PR helpers
    # ------------------------------------------------------------------

    def get_pr_files(self, pr_number: int) -> List[PullRequestFile]:
        """Return the list of files changed in a pull request."""
        url = f"{GITHUB_API_URL}/repos/{self.repo}/pulls/{pr_number}/files"
        response = self._session.get(url, params={"per_page": 100})
        response.raise_for_status()
        return [
            PullRequestFile(
                filename=f["filename"],
                additions=f["additions"],
                deletions=f["deletions"],
            )
            for f in response.json()
        ]

    def set_labels(self, pr_number: int, labels: List[str]) -> None:
        """Replace all labels on a pull request with *labels*."""
        url = f"{GITHUB_API_URL}/repos/{self.repo}/issues/{pr_number}/labels"
        response = self._session.put(url, json={"labels": labels})
        response.raise_for_status()


def client_from_env() -> GitHubClient:
    """Build a :class:`GitHubClient` from standard GitHub Actions env vars."""
    token = os.environ["GITHUB_TOKEN"]
    repo = os.environ["GITHUB_REPOSITORY"]
    return GitHubClient(token=token, repo=repo)
