"""Thin GitHub REST client used by the runner."""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import List

import requests

from src.cache import ResponseCache


@dataclass
class PullRequestFile:
    filename: str
    additions: int
    deletions: int

    @property
    def changes(self) -> int:
        return self.additions + self.deletions


class GitHubClient:
    """Minimal client for the GitHub Pull Requests API."""

    BASE_URL = "https://api.github.com"

    def __init__(
        self,
        token: str | None = None,
        cache: ResponseCache | None = None,
    ) -> None:
        self._token = token or os.environ.get("GITHUB_TOKEN", "")
        self._cache = cache or ResponseCache()
        self._session = requests.Session()
        self._session.headers.update(
            {
                "Authorization": f"Bearer {self._token}",
                "Accept": "application/vnd.github+json",
                "X-GitHub-Api-Version": "2022-11-28",
            }
        )

    def get_pr_files(self, repo: str, pr_number: int) -> List[PullRequestFile]:
        """Return files changed in *pr_number* for *repo* (owner/name)."""
        cache_key = f"{repo}/pulls/{pr_number}/files"
        cached = self._cache.get(cache_key)
        if cached is not None:
            return [PullRequestFile(**f) for f in cached]

        url = f"{self.BASE_URL}/repos/{repo}/pulls/{pr_number}/files"
        response = self._session.get(url, timeout=15)
        response.raise_for_status()
        raw: list = response.json()

        files = [
            PullRequestFile(
                filename=item["filename"],
                additions=item["additions"],
                deletions=item["deletions"],
            )
            for item in raw
        ]
        self._cache.set(cache_key, [{"filename": f.filename, "additions": f.additions, "deletions": f.deletions} for f in files])
        return files

    def set_labels(self, repo: str, pr_number: int, labels: List[str]) -> None:
        """Replace the labels on *pr_number* with *labels*."""
        url = f"{self.BASE_URL}/repos/{repo}/issues/{pr_number}/labels"
        response = self._session.put(url, json={"labels": labels}, timeout=15)
        response.raise_for_status()
