"""Tests for stashenv.env_mask."""

import pytest

from stashenv.env_mask import (
    MaskedLine,
    _is_sensitive,
    _mask_value,
    format_masked,
    mask_env_text,
)


# ---------------------------------------------------------------------------
# _is_sensitive
# ---------------------------------------------------------------------------

def test_is_sensitive_detects_secret():
    assert _is_sensitive("MY_SECRET") is True


def test_is_sensitive_detects_password():
    assert _is_sensitive("DB_PASSWORD") is True


def test_is_sensitive_detects_token():
    assert _is_sensitive("GITHUB_TOKEN") is True


def test_is_sensitive_safe_key_returns_false():
    assert _is_sensitive("APP_ENV") is False


def test_is_sensitive_extra_pattern():
    assert _is_sensitive("MY_CERT", extra_patterns=["CERT"]) is True


# ---------------------------------------------------------------------------
# _mask_value
# ---------------------------------------------------------------------------

def test_mask_value_short_string():
    result = _mask_value("abc")
    assert result == "*" * 8


def test_mask_value_long_string_shows_prefix():
    result = _mask_value("supersecret")
    assert result.startswith("su")
    assert "*" in result


def test_mask_value_empty_string_unchanged():
    assert _mask_value("") == ""


# ---------------------------------------------------------------------------
# mask_env_text
# ---------------------------------------------------------------------------

SAMPLE = """
APP_ENV=production
DB_PASSWORD=hunter2
API_KEY=abc123xyz
PORT=8080
# a comment
EMPTY=
"""


def test_mask_env_text_returns_correct_count():
    lines = mask_env_text(SAMPLE)
    assert len(lines) == 5


def test_mask_env_text_masks_password():
    lines = mask_env_text(SAMPLE)
    entry = next(e for e in lines if e.key == "DB_PASSWORD")
    assert entry.is_masked is True
    assert entry.masked_value != entry.raw_value


def test_mask_env_text_does_not_mask_safe_key():
    lines = mask_env_text(SAMPLE)
    entry = next(e for e in lines if e.key == "PORT")
    assert entry.is_masked is False
    assert entry.masked_value == "8080"


def test_mask_env_text_skips_comments_and_blanks():
    lines = mask_env_text(SAMPLE)
    keys = [e.key for e in lines]
    assert "# a comment" not in keys


def test_mask_env_text_show_keys_overrides_mask():
    lines = mask_env_text(SAMPLE, show_keys=["API_KEY"])
    entry = next(e for e in lines if e.key == "API_KEY")
    assert entry.is_masked is False


def test_mask_env_text_extra_patterns():
    text = "STRIPE_CERT=abc123\nHOST=localhost\n"
    lines = mask_env_text(text, extra_patterns=["CERT"])
    cert_entry = next(e for e in lines if e.key == "STRIPE_CERT")
    assert cert_entry.is_masked is True


# ---------------------------------------------------------------------------
# format_masked
# ---------------------------------------------------------------------------

def test_format_masked_appends_indicator():
    lines = mask_env_text(SAMPLE)
    output = format_masked(lines)
    assert "[masked]" in output


def test_format_masked_reveal_shows_raw_values():
    lines = mask_env_text(SAMPLE)
    output = format_masked(lines, reveal=True)
    assert "hunter2" in output
    assert "[masked]" not in output


def test_format_masked_safe_key_no_indicator():
    lines = mask_env_text(SAMPLE)
    output = format_masked(lines)
    assert "PORT=8080" in output
