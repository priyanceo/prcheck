"""Tests for src/label_rollback.py and src/rollback_config.py."""
from __future__ import annotations

from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

import pytest

from src.audit_log import AuditEntry, AuditLog
from src.label_rollback import RollbackResult, run_rollback
from src.rollback_config import RollbackConfig, parse_rollback_config


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_entry(pr_number: int, actions: list, ts: str = "2024-01-01T00:00:00+00:00") -> AuditEntry:
    entry = MagicMock(spec=AuditEntry)
    entry.pr_number = pr_number
    entry.timestamp = ts
    entry.actions = actions
    return entry


def _make_audit_log(entries: list) -> AuditLog:
    log = MagicMock(spec=AuditLog)
    log.entries_for_pr = MagicMock(return_value=entries)
    return log


# ---------------------------------------------------------------------------
# RollbackResult
# ---------------------------------------------------------------------------

class TestRollbackResult:
    def test_success_true_when_no_error(self):
        r = RollbackResult(pr_number=1, repo="org/repo")
        assert r.success is True

    def test_success_false_when_error_set(self):
        r = RollbackResult(pr_number=1, repo="org/repo", error="boom")
        assert r.success is False

    def test_to_dict_contains_expected_keys(self):
        r = RollbackResult(pr_number=7, repo="org/repo", removed=["bug"], skipped=[])
        d = r.to_dict()
        assert d["pr_number"] == 7
        assert d["removed"] == ["bug"]
        assert d["success"] is True


# ---------------------------------------------------------------------------
# run_rollback
# ---------------------------------------------------------------------------

class TestRunRollback:
    def test_skips_all_when_no_audit_entries(self):
        client = MagicMock()
        log = _make_audit_log([])
        result = run_rollback(42, "org/repo", log, client)
        assert result.skipped == ["*"]
        client.remove_label.assert_not_called()

    def test_removes_labels_from_latest_entry(self):
        actions = [{"action": "added", "label": "bug"}, {"action": "added", "label": "enhancement"}]
        entry = _make_entry(1, actions, "2024-06-01T00:00:00+00:00")
        log = _make_audit_log([entry])
        client = MagicMock()
        result = run_rollback(1, "org/repo", log, client)
        assert sorted(result.removed) == ["bug", "enhancement"]
        assert client.remove_label.call_count == 2

    def test_dry_run_does_not_call_client(self):
        actions = [{"action": "added", "label": "size/large"}]
        entry = _make_entry(5, actions)
        log = _make_audit_log([entry])
        client = MagicMock()
        result = run_rollback(5, "org/repo", log, client, dry_run=True)
        assert result.removed == ["size/large"]
        client.remove_label.assert_not_called()

    def test_skips_label_on_client_error(self):
        actions = [{"action": "added", "label": "wip"}]
        entry = _make_entry(3, actions)
        log = _make_audit_log([entry])
        client = MagicMock()
        client.remove_label.side_effect = RuntimeError("API error")
        result = run_rollback(3, "org/repo", log, client)
        assert "wip" in result.skipped
        assert result.error == "API error"

    def test_ignores_non_added_actions(self):
        actions = [{"action": "removed", "label": "bug"}]
        entry = _make_entry(9, actions)
        log = _make_audit_log([entry])
        client = MagicMock()
        result = run_rollback(9, "org/repo", log, client)
        assert result.removed == []
        client.remove_label.assert_not_called()


# ---------------------------------------------------------------------------
# parse_rollback_config
# ---------------------------------------------------------------------------

class TestParseRollbackConfigDefaults:
    def test_empty_config_returns_defaults(self):
        cfg = parse_rollback_config({})
        assert cfg.enabled is False
        assert cfg.dry_run is False
        assert cfg.max_labels_per_run == 20

    def test_missing_rollback_key_returns_defaults(self):
        cfg = parse_rollback_config({"other": True})
        assert isinstance(cfg, RollbackConfig)

    def test_non_dict_rollback_section_returns_defaults(self):
        cfg = parse_rollback_config({"rollback": "yes"})
        assert cfg.enabled is False


class TestParseRollbackConfigValues:
    def test_enabled_true(self):
        cfg = parse_rollback_config({"rollback": {"enabled": True}})
        assert cfg.enabled is True

    def test_dry_run_true(self):
        cfg = parse_rollback_config({"rollback": {"dry_run": True}})
        assert cfg.dry_run is True

    def test_max_labels_per_run_set(self):
        cfg = parse_rollback_config({"rollback": {"max_labels_per_run": 5}})
        assert cfg.max_labels_per_run == 5

    def test_invalid_max_labels_falls_back_to_default(self):
        cfg = parse_rollback_config({"rollback": {"max_labels_per_run": -3}})
        assert cfg.max_labels_per_run == 20
