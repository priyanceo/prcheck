"""Thin GitHub REST API client used by the runner."""

from __future__ import annotations

import os
import logging
from dataclasses import dataclass
from typing import List

import requests

from src.retry import RetryConfig, with_retry

logger = logging.getLogger(__name__)

_RETRY_CFG = RetryConfig(
    max_attempts=3,
    base_delay=1.0,
    backoff_factor=2.0,
    max_delay=15.0,
    retryable_exceptions=(requests.exceptions.ConnectionError, requests.exceptions.Timeout),
)


@dataclass
class PullRequestFile:
    filename: str
    additions: int
    deletions: int

    @property
    def changes(self) -> int:
        return self.additions + self.deletions


class GitHubClient:
    BASE_URL = "https://api.github.com"

    def __init__(self, token: str | None = None) -> None:
        self._token = token or os.environ.get("GITHUB_TOKEN", "")
        self._session = requests.Session()
        self._session.headers.update(
            {
                "Authorization": f"Bearer {self._token}",
                "Accept": "application/vnd.github+json",
                "X-GitHub-Api-Version": "2022-11-28",
            }
        )

    def get_pr_files(self, owner: str, repo: str, pr_number: int) -> List[PullRequestFile]:
        url = f"{self.BASE_URL}/repos/{owner}/{repo}/pulls/{pr_number}/files"
        logger.debug("Fetching PR files from %s", url)

        def _fetch() -> List[PullRequestFile]:
            resp = self._session.get(url, timeout=10)
            resp.raise_for_status()
            return [
                PullRequestFile(
                    filename=f["filename"],
                    additions=f["additions"],
                    deletions=f["deletions"],
                )
                for f in resp.json()
            ]

        return with_retry(_fetch, _RETRY_CFG)

    def set_pr_labels(self, owner: str, repo: str, pr_number: int, labels: List[str]) -> None:
        url = f"{self.BASE_URL}/repos/{owner}/{repo}/issues/{pr_number}/labels"
        logger.debug("Setting labels %s on PR #%d", labels, pr_number)

        def _post() -> None:
            resp = self._session.post(url, json={"labels": labels}, timeout=10)
            resp.raise_for_status()

        with_retry(_post, _RETRY_CFG)
