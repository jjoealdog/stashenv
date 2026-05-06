"""Tests for stashenv.env_stats."""
import pytest
from stashenv.env_stats import compute_stats, format_stats

SIMPLE = """\
DB_HOST=localhost
DB_PORT=5432
DB_NAME=mydb
"""

WITH_EXTRAS = """\
# database settings
DB_HOST=localhost
DB_PORT=5432
EMPTY_VAL=

LONG_VALUE_KEY=this_is_a_rather_long_value_string
DB_HOST=duplicate
"""


def test_total_keys_counted():
    stats = compute_stats("simple", SIMPLE)
    assert stats.total_keys == 3


def test_empty_values_detected():
    stats = compute_stats("extras", WITH_EXTRAS)
    assert stats.empty_values == 1


def test_comment_lines_counted():
    stats = compute_stats("extras", WITH_EXTRAS)
    assert stats.comment_lines == 1


def test_blank_lines_counted():
    stats = compute_stats("extras", WITH_EXTRAS)
    assert stats.blank_lines == 1


def test_duplicate_keys_detected():
    stats = compute_stats("extras", WITH_EXTRAS)
    assert "DB_HOST" in stats.duplicate_keys


def test_no_duplicates_in_simple():
    stats = compute_stats("simple", SIMPLE)
    assert stats.duplicate_keys == []


def test_longest_key():
    stats = compute_stats("extras", WITH_EXTRAS)
    assert stats.longest_key == "LONG_VALUE_KEY"


def test_longest_value_key():
    stats = compute_stats("extras", WITH_EXTRAS)
    assert stats.longest_value_key == "LONG_VALUE_KEY"


def test_avg_value_length_positive():
    stats = compute_stats("simple", SIMPLE)
    assert stats.avg_value_length > 0


def test_empty_text_gives_zero_keys():
    stats = compute_stats("empty", "")
    assert stats.total_keys == 0
    assert stats.avg_value_length == 0.0


def test_format_stats_contains_profile_name():
    stats = compute_stats("myprofile", SIMPLE)
    output = format_stats(stats)
    assert "myprofile" in output


def test_format_stats_shows_key_count():
    stats = compute_stats("simple", SIMPLE)
    output = format_stats(stats)
    assert "3" in output


def test_format_stats_shows_no_dupes_label():
    stats = compute_stats("simple", SIMPLE)
    output = format_stats(stats)
    assert "none" in output


def test_value_with_equals_sign():
    text = "URL=http://example.com?a=1&b=2\n"
    stats = compute_stats("url", text)
    assert stats.total_keys == 1
    assert stats.avg_value_length == len("http://example.com?a=1&b=2")
