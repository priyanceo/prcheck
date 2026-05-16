"""Parse rollback configuration from the prcheck config dict."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict


@dataclass
class RollbackConfig:
    enabled: bool = False
    dry_run: bool = False
    max_labels_per_run: int = 20

    def __post_init__(self) -> None:
        if not isinstance(self.enabled, bool):
            raise TypeError(f"enabled must be bool, got {type(self.enabled).__name__}")
        if not isinstance(self.dry_run, bool):
            raise TypeError(f"dry_run must be bool, got {type(self.dry_run).__name__}")
        if not isinstance(self.max_labels_per_run, int) or self.max_labels_per_run < 1:
            raise ValueError(
                f"max_labels_per_run must be a positive int, got {self.max_labels_per_run!r}"
            )


def parse_rollback_config(config: Dict[str, Any]) -> RollbackConfig:
    """Return a RollbackConfig from the top-level config dict.

    Accepts::

        rollback:
          enabled: true
          dry_run: false
          max_labels_per_run: 10
    """
    section = config.get("rollback")
    if not isinstance(section, dict):
        return RollbackConfig()

    enabled = section.get("enabled", False)
    if not isinstance(enabled, bool):
        enabled = False

    dry_run = section.get("dry_run", False)
    if not isinstance(dry_run, bool):
        dry_run = False

    max_labels = section.get("max_labels_per_run", 20)
    if not isinstance(max_labels, int) or max_labels < 1:
        max_labels = 20

    return RollbackConfig(enabled=enabled, dry_run=dry_run, max_labels_per_run=max_labels)
