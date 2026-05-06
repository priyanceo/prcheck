"""Parses notification-related settings from the prcheck config file."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class NotificationConfig:
    enabled: bool = True
    output_path: Optional[str] = None
    log_level: str = "INFO"


def parse_notification_config(raw: dict) -> NotificationConfig:
    """Extract notification settings from the top-level config dict.

    Expected shape (all keys optional)::

        notifications:
          enabled: true
          output_path: /tmp/prcheck_notifications.jsonl
          log_level: DEBUG
    """
    section = raw.get("notifications", {})
    if not isinstance(section, dict):
        raise ValueError("'notifications' must be a mapping")

    enabled = section.get("enabled", True)
    if not isinstance(enabled, bool):
        raise ValueError("'notifications.enabled' must be a boolean")

    output_path = section.get("output_path", None)
    if output_path is not None and not isinstance(output_path, str):
        raise ValueError("'notifications.output_path' must be a string")

    log_level = section.get("log_level", "INFO")
    if log_level not in {"DEBUG", "INFO", "WARNING", "ERROR"}:
        raise ValueError(
            f"'notifications.log_level' must be one of DEBUG/INFO/WARNING/ERROR, got {log_level!r}"
        )

    return NotificationConfig(
        enabled=enabled,
        output_path=output_path,
        log_level=log_level,
    )
