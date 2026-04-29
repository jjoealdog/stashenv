"""Tests for stashenv/cli_expire.py"""

import pytest
from click.testing import CliRunner
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import patch

from stashenv.cli_expire import expire_group
from stashenv.expire import set_expiry, get_expiry


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def store(tmp_path):
    with patch("stashenv.cli_expire._store_dir", return_value=tmp_path):
        yield tmp_path


def _future_str(days=1):
    dt = datetime.now(timezone.utc) + timedelta(days=days)
    return dt.isoformat()


def _past_str(days=1):
    dt = datetime.now(timezone.utc) - timedelta(days=days)
    return dt.isoformat()


def test_set_cmd_sets_expiry(runner, store):
    result = runner.invoke(expire_group, ["set", "dev", _future_str()])
    assert result.exit_code == 0
    assert "dev" in result.output
    assert get_expiry(store, "dev") is not None


def test_set_cmd_invalid_date_exits_nonzero(runner, store):
    result = runner.invoke(expire_group, ["set", "dev", "not-a-date"])
    assert result.exit_code != 0
    assert "invalid datetime" in result.output


def test_clear_cmd_removes_expiry(runner, store):
    set_expiry(store, "dev", datetime.now(timezone.utc) + timedelta(days=1))
    result = runner.invoke(expire_group, ["clear", "dev"])
    assert result.exit_code == 0
    assert "cleared" in result.output
    assert get_expiry(store, "dev") is None


def test_clear_cmd_no_expiry_set(runner, store):
    result = runner.invoke(expire_group, ["clear", "dev"])
    assert result.exit_code == 0
    assert "No expiry was set" in result.output


def test_get_cmd_shows_active(runner, store):
    set_expiry(store, "dev", datetime.now(timezone.utc) + timedelta(days=5))
    result = runner.invoke(expire_group, ["get", "dev"])
    assert result.exit_code == 0
    assert "active" in result.output


def test_get_cmd_shows_expired(runner, store):
    set_expiry(store, "dev", datetime.now(timezone.utc) - timedelta(days=1))
    result = runner.invoke(expire_group, ["get", "dev"])
    assert result.exit_code == 0
    assert "EXPIRED" in result.output


def test_get_cmd_no_expiry(runner, store):
    result = runner.invoke(expire_group, ["get", "dev"])
    assert result.exit_code == 0
    assert "No expiry set" in result.output


def test_list_cmd_empty(runner, store):
    result = runner.invoke(expire_group, ["list"])
    assert result.exit_code == 0
    assert "No expiry dates set" in result.output


def test_list_cmd_shows_entries(runner, store):
    set_expiry(store, "dev", datetime.now(timezone.utc) + timedelta(days=2))
    set_expiry(store, "prod", datetime.now(timezone.utc) - timedelta(days=1))
    result = runner.invoke(expire_group, ["list"])
    assert result.exit_code == 0
    assert "dev" in result.output
    assert "prod" in result.output
    assert "EXPIRED" in result.output
    assert "active" in result.output
