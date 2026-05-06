"""Tests for src/github_client.py"""

import pytest
from unittest.mock import MagicMock, patch

from src.github_client import GitHubClient, PullRequestFile


@pytest.fixture()
def client():
    return GitHubClient(token="test-token")


class TestPullRequestFile:
    def test_changes_sums_additions_and_deletions(self):
        f = PullRequestFile(filename="a.py", additions=10, deletions=3)
        assert f.changes == 13

    def test_changes_zero_when_no_edits(self):
        f = PullRequestFile(filename="b.py", additions=0, deletions=0)
        assert f.changes == 0


class TestGetPrFiles:
    def _mock_response(self, data):
        resp = MagicMock()
        resp.json.return_value = data
        resp.raise_for_status.return_value = None
        return resp

    def test_returns_list_of_pr_files(self, client):
        payload = [
            {"filename": "src/foo.py", "additions": 5, "deletions": 2},
            {"filename": "README.md", "additions": 1, "deletions": 0},
        ]
        with patch.object(client._session, "get", return_value=self._mock_response(payload)):
            files = client.get_pr_files("owner", "repo", 42)

        assert len(files) == 2
        assert files[0].filename == "src/foo.py"
        assert files[0].additions == 5
        assert files[1].filename == "README.md"

    def test_empty_response_returns_empty_list(self, client):
        with patch.object(client._session, "get", return_value=self._mock_response([])):
            files = client.get_pr_files("owner", "repo", 1)
        assert files == []

    def test_raises_on_http_error(self, client):
        import requests

        resp = MagicMock()
        resp.raise_for_status.side_effect = requests.exceptions.HTTPError("404")
        with patch.object(client._session, "get", return_value=resp):
            with pytest.raises(requests.exceptions.HTTPError):
                client.get_pr_files("owner", "repo", 99)


class TestSetPrLabels:
    def test_posts_labels_successfully(self, client):
        resp = MagicMock()
        resp.raise_for_status.return_value = None
        with patch.object(client._session, "post", return_value=resp) as mock_post:
            client.set_pr_labels("owner", "repo", 7, ["bug", "size/S"])
        mock_post.assert_called_once()
        _, kwargs = mock_post.call_args
        assert kwargs["json"] == {"labels": ["bug", "size/S"]}

    def test_raises_on_http_error(self, client):
        import requests

        resp = MagicMock()
        resp.raise_for_status.side_effect = requests.exceptions.HTTPError("403")
        with patch.object(client._session, "post", return_value=resp):
            with pytest.raises(requests.exceptions.HTTPError):
                client.set_pr_labels("owner", "repo", 7, ["bug"])
