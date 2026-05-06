"""Unit tests for src/metrics_reporter.py."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from src.metrics import RunMetrics
from src.metrics_reporter import MetricsReporter


@pytest.fixture()
def reporter(tmp_path: Path) -> MetricsReporter:
    return MetricsReporter(log_path=tmp_path / "metrics.jsonl")


class TestMetricsReporterRecord:
    def test_creates_file_on_first_record(self, reporter: MetricsReporter):
        m = RunMetrics(pr_number=1)
        m.finish()
        reporter.record(m)
        assert reporter.log_path.exists()

    def test_appends_valid_json_lines(self, reporter: MetricsReporter):
        for pr in (10, 20):
            m = RunMetrics(pr_number=pr)
            m.finish()
            reporter.record(m)
        lines = reporter.log_path.read_text().strip().splitlines()
        assert len(lines) == 2
        for line in lines:
            json.loads(line)  # must not raise

    def test_pr_number_persisted(self, reporter: MetricsReporter):
        m = RunMetrics(pr_number=55)
        m.finish()
        reporter.record(m)
        data = json.loads(reporter.log_path.read_text().strip())
        assert data["pr_number"] == 55


class TestMetricsReporterReadAll:
    def test_empty_when_no_file(self, reporter: MetricsReporter):
        assert reporter.read_all() == []

    def test_round_trip(self, reporter: MetricsReporter):
        m = RunMetrics(pr_number=3, files_evaluated=5, total_changes=120)
        m.labels_added = ["backend"]
        m.finish()
        reporter.record(m)
        records = reporter.read_all()
        assert len(records) == 1
        assert records[0].pr_number == 3
        assert records[0].files_evaluated == 5
        assert records[0].total_changes == 120
        assert records[0].labels_added == ["backend"]

    def test_multiple_records_order(self, reporter: MetricsReporter):
        for pr in (1, 2, 3):
            m = RunMetrics(pr_number=pr)
            m.finish()
            reporter.record(m)
        records = reporter.read_all()
        assert [r.pr_number for r in records] == [1, 2, 3]


class TestMetricsReporterLatest:
    def test_latest_none_when_empty(self, reporter: MetricsReporter):
        assert reporter.latest() is None

    def test_latest_returns_last(self, reporter: MetricsReporter):
        for pr in (7, 8, 9):
            m = RunMetrics(pr_number=pr)
            m.finish()
            reporter.record(m)
        assert reporter.latest().pr_number == 9
