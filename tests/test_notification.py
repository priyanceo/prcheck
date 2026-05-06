"""Tests for src/notification.py."""
from __future__ import annotations

import json
import os
import pytest

from src.notification import LabelAction, PRNotification, NotificationService


# ---------------------------------------------------------------------------
# LabelAction
# ---------------------------------------------------------------------------

class TestLabelAction:
    def test_to_dict_contains_expected_keys(self):
        action = LabelAction(label="bug", action="added", reason="matches src/")
        d = action.to_dict()
        assert d["label"] == "bug"
        assert d["action"] == "added"
        assert d["reason"] == "matches src/"


# ---------------------------------------------------------------------------
# PRNotification
# ---------------------------------------------------------------------------

class TestPRNotification:
    def _make_notification(self) -> PRNotification:
        return PRNotification(pr_number=42, repo="org/repo")

    def test_initial_actions_empty(self):
        n = self._make_notification()
        assert n.actions == []

    def test_add_action_appends(self):
        n = self._make_notification()
        n.add_action("bug", "added", "reason")
        assert len(n.actions) == 1
        assert n.actions[0].label == "bug"

    def test_to_dict_structure(self):
        n = self._make_notification()
        n.add_action("size/large", "added", "diff > 500")
        d = n.to_dict()
        assert d["pr_number"] == 42
        assert d["repo"] == "org/repo"
        assert len(d["actions"]) == 1
        assert "timestamp" in d

    def test_format_summary_no_actions(self):
        n = self._make_notification()
        assert "no label changes" in n.format_summary()

    def test_format_summary_with_actions(self):
        n = self._make_notification()
        n.add_action("bug", "added", "matched")
        summary = n.format_summary()
        assert "[ADDED]" in summary
        assert "bug" in summary


# ---------------------------------------------------------------------------
# NotificationService
# ---------------------------------------------------------------------------

class TestNotificationService:
    def test_send_without_output_path_does_not_raise(self):
        svc = NotificationService()
        n = PRNotification(pr_number=1, repo="a/b")
        n.add_action("bug", "added", "test")
        svc.send(n)  # should not raise

    def test_send_writes_json_line(self, tmp_path):
        out = tmp_path / "notifications.jsonl"
        svc = NotificationService(output_path=str(out))
        n = PRNotification(pr_number=7, repo="a/b")
        n.add_action("size/small", "added", "diff < 50")
        svc.send(n)
        lines = out.read_text().strip().splitlines()
        assert len(lines) == 1
        data = json.loads(lines[0])
        assert data["pr_number"] == 7

    def test_send_appends_multiple_notifications(self, tmp_path):
        out = tmp_path / "notifications.jsonl"
        svc = NotificationService(output_path=str(out))
        for pr in (1, 2, 3):
            n = PRNotification(pr_number=pr, repo="a/b")
            svc.send(n)
        lines = out.read_text().strip().splitlines()
        assert len(lines) == 3
