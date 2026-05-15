"""Tests for src/grouping_config.py."""
from src.grouping_config import parse_grouping_config


class TestParseGroupingConfigDefaults:
    def test_empty_config_returns_resolver(self):
        resolver = parse_grouping_config({})
        assert resolver.resolve("x").matched is False

    def test_missing_grouping_key_returns_defaults(self):
        resolver = parse_grouping_config({"other": []})
        assert resolver.resolve("ci/build").matched is False

    def test_non_list_grouping_section_returns_defaults(self):
        resolver = parse_grouping_config({"grouping": "bad"})
        assert resolver.resolve("ci/build").matched is False

    def test_non_dict_entry_skipped(self):
        resolver = parse_grouping_config({"grouping": ["not-a-dict"]})
        assert resolver.resolve("ci/build").matched is False

    def test_entry_without_members_skipped(self):
        resolver = parse_grouping_config({"grouping": [{"group": "ci"}]})
        assert resolver.resolve("ci/build").matched is False

    def test_empty_members_list_skipped(self):
        resolver = parse_grouping_config({"grouping": [{"group": "ci", "members": []}]})
        assert resolver.resolve("ci/build").matched is False


class TestParseGroupingConfigValues:
    def _config(self):
        return {
            "grouping": [
                {"group": "ci", "members": ["ci/build", "ci/test"]},
                {"group": "docs", "members": ["documentation", "readme"]},
            ]
        }

    def test_known_label_resolves(self):
        resolver = parse_grouping_config(self._config())
        result = resolver.resolve("ci/build")
        assert result.matched is True
        assert result.group == "ci"

    def test_second_group_resolves(self):
        resolver = parse_grouping_config(self._config())
        result = resolver.resolve("readme")
        assert result.matched is True
        assert result.group == "docs"

    def test_unknown_label_not_matched(self):
        resolver = parse_grouping_config(self._config())
        assert resolver.resolve("security").matched is False

    def test_groups_for_labels_integration(self):
        resolver = parse_grouping_config(self._config())
        mapping = resolver.groups_for_labels(["ci/build", "documentation", "unknown"])
        assert mapping.get("ci") == ["ci/build"]
        assert mapping.get("docs") == ["documentation"]
