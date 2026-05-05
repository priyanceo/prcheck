"""Parse prcheck YAML configuration into Labeler rules."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

import yaml

from .labeler import LabelRule, Labeler, SizeRule

_DEFAULT_CONFIG_PATH = ".github/prcheck.yml"


def _parse_path_rules(raw: Dict[str, Any]) -> list[LabelRule]:
    rules: list[LabelRule] = []
    for label, patterns in raw.items():
        if not isinstance(patterns, list):
            patterns = [patterns]
        rules.append(LabelRule(label=label, patterns=[str(p) for p in patterns]))
    return rules


def _parse_size_rules(raw: Dict[str, Any]) -> list[SizeRule]:
    rules: list[SizeRule] = []
    for label, bounds in raw.items():
        if not isinstance(bounds, dict):
            raise ValueError(
                f"Size rule '{label}' must be a mapping with 'min' and/or 'max' keys."
            )
        rules.append(
            SizeRule(
                label=label,
                min_lines=int(bounds.get("min", 0)),
                max_lines=int(bounds["max"]) if "max" in bounds else None,
            )
        )
    return rules


def load_config(path: str | Path = _DEFAULT_CONFIG_PATH) -> Labeler:
    """Load a prcheck YAML config file and return a configured :class:`Labeler`.

    Expected YAML structure::

        path-labels:
          documentation: ["docs/**", "*.md"]
          ci: [".github/**"]

        size-labels:
          size/XS:
            max: 10
          size/S:
            min: 11
            max: 50
          size/L:
            min: 51
    """
    config_path = Path(path)
    if not config_path.exists():
        raise FileNotFoundError(f"prcheck config not found: {config_path}")

    with config_path.open(encoding="utf-8") as fh:
        data: Dict[str, Any] = yaml.safe_load(fh) or {}

    path_rules = _parse_path_rules(data.get("path-labels", {}))
    size_rules = _parse_size_rules(data.get("size-labels", {}))
    return Labeler(path_rules=path_rules, size_rules=size_rules)
