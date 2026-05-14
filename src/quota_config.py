"""Parse quota configuration from the prcheck YAML config dict."""
from __future__ import annotations

from typing import Any, Dict

from src.label_quota import QuotaConfig

_DEFAULT_MAX_LABELS = 10
_DEFAULT_STRATEGY = "drop"


def parse_quota_config(config: Dict[str, Any]) -> QuotaConfig:
    """Extract and validate the *quota* section from the top-level config dict.

    Missing or malformed values fall back to safe defaults so that existing
    configs without a quota section continue to work unchanged.
    """
    section = config.get("quota")
    if not isinstance(section, dict):
        return QuotaConfig(
            max_labels=_DEFAULT_MAX_LABELS,
            overflow_strategy=_DEFAULT_STRATEGY,
        )

    raw_max = section.get("max_labels", _DEFAULT_MAX_LABELS)
    max_labels = int(raw_max) if isinstance(raw_max, int) and raw_max >= 1 else _DEFAULT_MAX_LABELS

    raw_strategy = section.get("overflow_strategy", _DEFAULT_STRATEGY)
    strategy = (
        raw_strategy
        if isinstance(raw_strategy, str) and raw_strategy in ("drop", "warn")
        else _DEFAULT_STRATEGY
    )

    return QuotaConfig(max_labels=max_labels, overflow_strategy=strategy)
