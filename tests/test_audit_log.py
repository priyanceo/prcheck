"""Tests for src/audit_log.py."""

from __future__ import annotations

import json
import os

import pytest

from src.audit_log import AuditEntry, AuditLog


@pytest.fixture
def log_path(tmp_path):
    return str(tmp_path / "audit.log")


@pytest.fixture
def audit_log(log_path):
    return AuditLog(log_path)


class TestAuditEntry:
    def test_to_dict_contains_expected_keys(self):
        entry = AuditEntry(
            pr_number=42,
            repo="org/repo",
            labels_added=["bug"],
            labels_removed=[],
        )
        d = entry.to_dict()
        assert d["pr_number"] == 42
        assert d["repo"] == "org/repo"
        assert d["labels_added"] == ["bug"]
        assert d["labels_removed"] == []
        assert "timestamp" in d

    def test_triggered_by_defaults_to_none(self):
        entry = AuditEntry(pr_number=1, repo="a/b", labels_added=[], labels_removed=[])
        assert entry.to_dict()["triggered_by"] is None

    def test_triggered_by_persisted(self):
        entry = AuditEntry(
            pr_number=1, repo="a/b", labels_added=[], labels_removed=[], triggered_by="ci"
        )
        assert entry.to_dict()["triggered_by"] == "ci"


class TestAuditLogRecord:
    def test_creates_file_on_first_record(self, audit_log, log_path):
        entry = AuditEntry(pr_number=1, repo="a/b", labels_added=["x"], labels_removed=[])
        audit_log.record(entry)
        assert os.path.exists(log_path)

    def test_appends_valid_json_lines(self, audit_log, log_path):
        for i in range(3):
            audit_log.record(
                AuditEntry(pr_number=i, repo="a/b", labels_added=["l"], labels_removed=[])
            )
        with open(log_path) as fh:
            lines = [l.strip() for l in fh if l.strip()]
        assert len(lines) == 3
        for line in lines:
            data = json.loads(line)
            assert "pr_number" in data

    def test_pr_number_persisted(self, audit_log):
        audit_log.record(
            AuditEntry(pr_number=99, repo="a/b", labels_added=[], labels_removed=[])
        )
        entries = audit_log.read_all()
        assert entries[0].pr_number == 99


class TestAuditLogReadAll:
    def test_returns_empty_list_when_no_file(self, log_path):
        log = AuditLog(log_path)
        assert log.read_all() == []

    def test_returns_all_entries(self, audit_log):
        audit_log.record(AuditEntry(pr_number=1, repo="a/b", labels_added=["a"], labels_removed=[]))
        audit_log.record(AuditEntry(pr_number=2, repo="a/b", labels_added=["b"], labels_removed=["a"]))
        entries = audit_log.read_all()
        assert len(entries) == 2
        assert entries[1].labels_removed == ["a"]

    def test_labels_added_roundtrip(self, audit_log):
        audit_log.record(
            AuditEntry(pr_number=7, repo="x/y", labels_added=["feat", "size:L"], labels_removed=[])
        )
        entry = audit_log.read_all()[0]
        assert entry.labels_added == ["feat", "size:L"]
