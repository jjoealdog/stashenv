"""Tests for stashenv.env_check."""

from pathlib import Path

import pytest

from stashenv.env_check import (
    CheckResult,
    check_profile,
    format_check_result,
    load_required_keys,
)


ENV_TEXT = "DB_HOST=localhost\nDB_PORT=5432\nSECRET_KEY=abc123\n"
REQUIRED = ["DB_HOST", "DB_PORT", "SECRET_KEY"]


def test_check_profile_all_present():
    result = check_profile("prod", ENV_TEXT, REQUIRED)
    assert result.ok
    assert result.missing == []


def test_check_profile_detects_missing_key():
    result = check_profile("prod", "DB_HOST=localhost\n", REQUIRED)
    assert not result.ok
    assert "DB_PORT" in result.missing
    assert "SECRET_KEY" in result.missing


def test_check_profile_detects_extra_keys():
    extra_env = ENV_TEXT + "EXTRA_KEY=oops\n"
    result = check_profile("dev", extra_env, REQUIRED)
    assert result.ok  # extra keys don't cause failure
    assert "EXTRA_KEY" in result.extra


def test_check_profile_ignores_comments_and_blank_lines():
    env = "# comment\n\nDB_HOST=x\nDB_PORT=5\nSECRET_KEY=s\n"
    result = check_profile("test", env, REQUIRED)
    assert result.ok
    assert "" not in result.missing


def test_check_profile_handles_value_with_equals():
    env = "DB_HOST=localhost\nDB_PORT=5432\nSECRET_KEY=a=b=c\n"
    result = check_profile("prod", env, REQUIRED)
    assert result.ok


def test_check_result_profile_name():
    result = check_profile("staging", ENV_TEXT, REQUIRED)
    assert result.profile == "staging"


def test_format_check_result_ok():
    result = CheckResult(profile="prod", missing=[], extra=[])
    output = format_check_result(result)
    assert "[OK]" in output
    assert "prod" in output


def test_format_check_result_fail_shows_missing():
    result = CheckResult(profile="dev", missing=["SECRET_KEY"], extra=[])
    output = format_check_result(result)
    assert "[FAIL]" in output
    assert "MISSING" in output
    assert "SECRET_KEY" in output


def test_format_check_result_shows_extra():
    result = CheckResult(profile="dev", missing=[], extra=["UNUSED"])
    output = format_check_result(result)
    assert "EXTRA" in output
    assert "UNUSED" in output


def test_load_required_keys(tmp_path: Path):
    schema = tmp_path / ".env.schema"
    schema.write_text("# required keys\nDB_HOST\nDB_PORT\n\nSECRET_KEY\n")
    keys = load_required_keys(schema)
    assert keys == ["DB_HOST", "DB_PORT", "SECRET_KEY"]
