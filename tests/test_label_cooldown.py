"""Tests for src/label_cooldown.py"""
from __future__ import annotations

import json
import time
from pathlib import Path

import pytest

from src.label_cooldown import CooldownConfig, CooldownResult, LabelCooldownStore


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture()
def store_path(tmp_path: Path) -> Path:
    return tmp_path / "cooldown.json"


@pytest.fixture()
def store(store_path: Path) -> LabelCooldownStore:
    return LabelCooldownStore(store_path)


# ---------------------------------------------------------------------------
# CooldownConfig
# ---------------------------------------------------------------------------

class TestCooldownConfig:
    def test_defaults(self):
        cfg = CooldownConfig()
        assert cfg.default_seconds == 0
        assert cfg.per_label == {}

    def test_negative_default_raises(self):
        with pytest.raises(ValueError, match="default_seconds"):
            CooldownConfig(default_seconds=-1)

    def test_negative_per_label_raises(self):
        with pytest.raises(ValueError, match="cooldown for"):
            CooldownConfig(per_label={"bug": -5})

    def test_seconds_for_falls_back_to_default(self):
        cfg = CooldownConfig(default_seconds=60)
        assert cfg.seconds_for("unknown") == 60

    def test_seconds_for_uses_per_label(self):
        cfg = CooldownConfig(default_seconds=60, per_label={"bug": 120})
        assert cfg.seconds_for("bug") == 120

    def test_seconds_for_normalises_label(self):
        cfg = CooldownConfig(per_label={"bug": 90})
        assert cfg.seconds_for(" Bug ") == 90


# ---------------------------------------------------------------------------
# CooldownResult
# ---------------------------------------------------------------------------

class TestCooldownResult:
    def test_to_dict_keys(self):
        r = CooldownResult(label="bug", allowed=True)
        d = r.to_dict()
        assert set(d.keys()) == {"label", "allowed", "remaining_seconds"}

    def test_to_dict_values(self):
        r = CooldownResult(label="wip", allowed=False, remaining_seconds=42.5)
        d = r.to_dict()
        assert d["label"] == "wip"
        assert d["allowed"] is False
        assert d["remaining_seconds"] == 42.5


# ---------------------------------------------------------------------------
# LabelCooldownStore
# ---------------------------------------------------------------------------

class TestLabelCooldownStore:
    def test_allowed_when_no_history(self, store: LabelCooldownStore):
        cfg = CooldownConfig(default_seconds=3600)
        result = store.check("bug", cfg)
        assert result.allowed is True

    def test_allowed_when_window_is_zero(self, store: LabelCooldownStore):
        store.record_removal("bug")
        cfg = CooldownConfig(default_seconds=0)
        result = store.check("bug", cfg)
        assert result.allowed is True

    def test_blocked_immediately_after_removal(self, store: LabelCooldownStore):
        store.record_removal("bug")
        cfg = CooldownConfig(default_seconds=3600)
        result = store.check("bug", cfg)
        assert result.allowed is False
        assert result.remaining_seconds > 0

    def test_allowed_after_window_expires(self, store_path: Path):
        s = LabelCooldownStore(store_path)
        s._data["bug"] = time.time() - 7200
        s._save()
        cfg = CooldownConfig(default_seconds=3600)
        result = s.check("bug", cfg)
        assert result.allowed is True

    def test_persists_across_instances(self, store_path: Path):
        s1 = LabelCooldownStore(store_path)
        s1.record_removal("wip")
        s2 = LabelCooldownStore(store_path)
        assert s2.last_removed_at("wip") is not None

    def test_corrupt_file_returns_empty(self, store_path: Path):
        store_path.write_text("not-json")
        s = LabelCooldownStore(store_path)
        assert s._data == {}
