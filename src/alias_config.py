"""Parse the *aliases* section of the prcheck YAML config into an AliasMap."""
from __future__ import annotations

from typing import Any, Dict

from src.label_alias import AliasMap


def parse_alias_config(config: Dict[str, Any]) -> AliasMap:
    """Build an :class:`AliasMap` from the top-level config dict.

    Expected shape::

        aliases:
          - alias: "bug"
            canonical: "bug-report"
          - alias: "feat"
            canonical: "feature"

    Unknown or malformed entries are silently skipped so that the rest of the
    pipeline continues to operate even with a partially-invalid config.
    """
    alias_map = AliasMap()

    section = config.get("aliases", [])
    if not isinstance(section, list):
        return alias_map

    for entry in section:
        if not isinstance(entry, dict):
            continue
        alias = entry.get("alias", "")
        canonical = entry.get("canonical", "")
        if not isinstance(alias, str) or not isinstance(canonical, str):
            continue
        try:
            alias_map.add(alias, canonical)
        except ValueError:
            continue

    return alias_map
