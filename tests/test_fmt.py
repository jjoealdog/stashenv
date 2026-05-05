"""Tests for stashenv.fmt."""
from __future__ import annotations

import pytest

from stashenv.fmt import format_env_text, FmtResult


# ---------------------------------------------------------------------------
# format_env_text
# ---------------------------------------------------------------------------

def test_clean_env_returns_unchanged():
    text = "FOO=bar\nBAZ=qux\n"
    result = format_env_text(text)
    assert not result.changed


def test_trailing_whitespace_removed():
    text = "FOO=bar   \nBAZ=qux\n"
    result = format_env_text(text)
    assert "   " not in result.formatted


def test_spaces_around_equals_normalised():
    text = "FOO = bar\n"
    result = format_env_text(text)
    assert "FOO=bar" in result.formatted
    assert result.changed


def test_multiple_blank_lines_collapsed():
    text = "FOO=bar\n\n\n\nBAZ=qux\n"
    result = format_env_text(text)
    # should have at most one consecutive blank line
    assert "\n\n\n" not in result.formatted
    assert result.changed


def test_single_blank_line_preserved():
    text = "FOO=bar\n\nBAZ=qux\n"
    result = format_env_text(text)
    assert "\n\n" in result.formatted


def test_sort_keys_alphabetical():
    text = "ZEBRA=1\nAPPLE=2\nMIDDLE=3\n"
    result = format_env_text(text, sort_keys=True)
    lines = [l for l in result.formatted.splitlines() if l.strip()]
    keys = [l.split("=")[0] for l in lines]
    assert keys == sorted(keys, key=str.lower)
    assert result.changed
    assert "sorted keys alphabetically" in result.changes


def test_sort_keys_already_sorted_still_flagged():
    text = "ALPHA=1\nBETA=2\n"
    result = format_env_text(text, sort_keys=True)
    # changes list still mentions sort even if order didn't change
    assert "sorted keys alphabetically" in result.changes


def test_strip_inline_comments():
    text = "FOO=bar # this is a comment\n"
    result = format_env_text(text, strip_inline_comments=True)
    assert "#" not in result.formatted
    assert result.changed
    assert any("FOO" in c for c in result.changes)


def test_strip_inline_comments_quoted_value_untouched():
    text = 'FOO="bar # not a comment"\n'
    result = format_env_text(text, strip_inline_comments=True)
    assert "not a comment" in result.formatted


def test_comment_lines_preserved():
    text = "# my comment\nFOO=bar\n"
    result = format_env_text(text)
    assert "# my comment" in result.formatted


def test_output_ends_with_newline():
    text = "FOO=bar"
    result = format_env_text(text)
    assert result.formatted.endswith("\n")


def test_fmt_result_changed_property():
    text = "FOO=bar\n"
    result = format_env_text(text)
    assert isinstance(result, FmtResult)
    assert result.changed == (result.original != result.formatted)


def test_empty_text_returns_newline():
    result = format_env_text("")
    assert result.formatted == "\n"
