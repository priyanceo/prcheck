"""Tests for src/runner.py — integration between config, client and labeler."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from src.github_client import PullRequestFile
from src.runner import _total_changes, run


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_file(filename: str, additions: int = 5, deletions: int = 3) -> PullRequestFile:
    return PullRequestFile(filename=filename, additions=additions, deletions=deletions)


SAMPLE_CONFIG = {
    "path_rules": [
        {"label": "python", "patterns": ["**/*.py"]},
        {"label": "docs", "patterns": ["docs/**"]},
    ],
    "size_rules": [
        {"label": "size/small", "max": 50},
        {"label": "size/large", "min": 200},
    ],
}


# ---------------------------------------------------------------------------
# Unit tests
# ---------------------------------------------------------------------------

class TestTotalChanges:
    def test_sums_additions_and_deletions(self):
        files = [_make_file("a.py", 10, 5), _make_file("b.py", 3, 2)]
        assert _total_changes(files) == 20

    def test_empty_list(self):
        assert _total_changes([]) == 0


class TestRun:
    def _make_client(self, files):
        client = MagicMock()
        client.get_pr_files.return_value = files
        return client

    @patch("src.runner.load_config", return_value=SAMPLE_CONFIG)
    def test_applies_matching_labels(self, mock_cfg):
        files = [_make_file("src/foo.py", additions=5, deletions=3)]
        client = self._make_client(files)

        labels = run(config_path=".github/prcheck.yml", pr_number=42, client=client)

        assert "python" in labels
        assert "size/small" in labels
        client.set_labels.assert_called_once_with(42, labels)

    @patch("src.runner.load_config", return_value=SAMPLE_CONFIG)
    def test_no_labels_skips_set_labels(self, mock_cfg):
        # A file that matches no path rule and a size not covered by any rule.
        files = [_make_file("assets/logo.png", additions=60, deletions=60)]
        client = self._make_client(files)

        labels = run(config_path=".github/prcheck.yml", pr_number=7, client=client)

        assert labels == []
        client.set_labels.assert_not_called()

    @patch("src.runner.load_config", return_value=SAMPLE_CONFIG)
    def test_docs_label_applied(self, mock_cfg):
        files = [_make_file("docs/guide.md", additions=10, deletions=0)]
        client = self._make_client(files)

        labels = run(config_path=".github/prcheck.yml", pr_number=99, client=client)

        assert "docs" in labels
