"""Persist and retrieve RunMetrics records."""
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import List, Optional

from src.metrics import RunMetrics

_DEFAULT_LOG_PATH = Path(os.getenv("PRCHECK_METRICS_FILE", "/tmp/prcheck_metrics.jsonl"))


class MetricsReporter:
    """Appends metric records as newline-delimited JSON."""

    def __init__(self, log_path: Path = _DEFAULT_LOG_PATH) -> None:
        self.log_path = log_path

    def record(self, metrics: RunMetrics) -> None:
        """Append *metrics* as a single JSON line to the log file."""
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        with self.log_path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(metrics.to_dict()) + "\n")

    def read_all(self) -> List[RunMetrics]:
        """Read and reconstruct all persisted RunMetrics records."""
        if not self.log_path.exists():
            return []
        records: List[RunMetrics] = []
        with self.log_path.open(encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                data = json.loads(line)
                m = RunMetrics(
                    pr_number=data["pr_number"],
                    files_evaluated=data.get("files_evaluated", 0),
                    total_changes=data.get("total_changes", 0),
                )
                m.labels_added = data.get("labels_added", [])
                m.labels_removed = data.get("labels_removed", [])
                records.append(m)
        return records

    def latest(self) -> Optional[RunMetrics]:
        """Return the most recently recorded RunMetrics, or None."""
        records = self.read_all()
        return records[-1] if records else None
