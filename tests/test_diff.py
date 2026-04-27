"""Tests for stashenv.diff module."""

import pytest
from stashenv.diff import parse_env_text, diff_profiles, format_diff, DiffEntry


ENV_A = """
DB_HOST=localhost
DB_PORT=5432
SECRET_KEY=abc123
DEBUG=true
"""

ENV_B = """
DB_HOST=prod.example.com
DB_PORT=5432
NEW_VAR=hello
DEBUG=false
"""


def test_parse_env_text_basic():
    result = parse_env_text("FOO=bar\nBAZ=qux")
    assert result == {"FOO": "bar", "BAZ": "qux"}


def test_parse_env_text_ignores_comments():
    result = parse_env_text("# comment\nFOO=bar")
    assert "# comment" not in result
    assert result["FOO"] == "bar"


def test_parse_env_text_ignores_blank_lines():
    result = parse_env_text("\n\nFOO=bar\n\n")
    assert result == {"FOO": "bar"}


def test_parse_env_text_handles_equals_in_value():
    result = parse_env_text("TOKEN=abc=def=")
    assert result["TOKEN"] == "abc=def="


def test_diff_detects_added_keys():
    entries = diff_profiles(ENV_A, ENV_B)
    statuses = {e.key: e.status for e in entries}
    assert statuses["NEW_VAR"] == "added"


def test_diff_detects_removed_keys():
    entries = diff_profiles(ENV_A, ENV_B)
    statuses = {e.key: e.status for e in entries}
    assert statuses["SECRET_KEY"] == "removed"


def test_diff_detects_changed_keys():
    entries = diff_profiles(ENV_A, ENV_B)
    statuses = {e.key: e.status for e in entries}
    assert statuses["DB_HOST"] == "changed"
    assert statuses["DEBUG"] == "changed"


def test_diff_detects_unchanged_keys():
    entries = diff_profiles(ENV_A, ENV_B)
    statuses = {e.key: e.status for e in entries}
    assert statuses["DB_PORT"] == "unchanged"


def test_diff_show_values_populates_fields():
    entries = diff_profiles(ENV_A, ENV_B, show_values=True)
    changed = next(e for e in entries if e.key == "DB_HOST")
    assert changed.left_value == "localhost"
    assert changed.right_value == "prod.example.com"


def test_diff_no_show_values_hides_fields():
    entries = diff_profiles(ENV_A, ENV_B, show_values=False)
    changed = next(e for e in entries if e.key == "DB_HOST")
    assert changed.left_value is None
    assert changed.right_value is None


def test_format_diff_contains_symbols():
    entries = diff_profiles(ENV_A, ENV_B)
    output = format_diff(entries)
    assert "+" in output
    assert "-" in output
    assert "~" in output


def test_format_diff_with_values():
    entries = diff_profiles(ENV_A, ENV_B, show_values=True)
    output = format_diff(entries, show_values=True)
    assert "->" in output
