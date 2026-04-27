"""Tests for stashenv/cli_history.py"""

import pytest
from click.testing import CliRunner
from pathlib import Path
from unittest.mock import patch

from stashenv.cli_history import history_group
from stashenv.history import snapshot_profile
from stashenv.crypto import encrypt


PASSWORD = "hunter2"
ENV_TEXT = b"API_KEY=abc123\nDEBUG=true\n"


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def store(tmp_path):
    with patch("stashenv.cli_history._store_dir", return_value=tmp_path), \
         patch("stashenv.cli_history._profile_path",
               side_effect=lambda d, p: d / f"{p}.env.enc"):
        yield tmp_path


def _make_snapshot(store_dir, profile, data=ENV_TEXT, password=PASSWORD):
    blob = encrypt(data, password)
    return snapshot_profile(store_dir, profile, blob, note="test snap")


def test_list_cmd_empty(runner, store):
    result = runner.invoke(history_group, ["list", "dev"])
    assert result.exit_code == 0
    assert "No history" in result.output


def test_list_cmd_shows_snapshots(runner, store):
    _make_snapshot(store, "dev")
    _make_snapshot(store, "dev")
    result = runner.invoke(history_group, ["list", "dev"])
    assert result.exit_code == 0
    assert "v2" in result.output
    assert "v1" in result.output
    assert "2 snapshot(s)" in result.output


def test_list_cmd_shows_note(runner, store):
    _make_snapshot(store, "dev")
    result = runner.invoke(history_group, ["list", "dev"])
    assert "test snap" in result.output


def test_restore_cmd_missing_snapshot_exits_nonzero(runner, store):
    result = runner.invoke(history_group, ["restore", "dev", "99"], input=PASSWORD)
    assert result.exit_code != 0
    assert "not found" in result.output


def test_restore_cmd_wrong_password_exits_nonzero(runner, store):
    _make_snapshot(store, "dev")
    result = runner.invoke(history_group, ["restore", "dev", "1"], input="wrongpassword")
    assert result.exit_code != 0
    assert "Decryption failed" in result.output


def test_restore_cmd_success(runner, store):
    _make_snapshot(store, "dev")
    result = runner.invoke(history_group, ["restore", "dev", "1"], input=PASSWORD)
    assert result.exit_code == 0
    assert "Restored" in result.output
    assert "v1" in result.output


def test_clear_cmd_removes_history(runner, store):
    _make_snapshot(store, "dev")
    _make_snapshot(store, "dev")
    result = runner.invoke(history_group, ["clear", "dev"], input="y")
    assert result.exit_code == 0
    assert "2 snapshot(s)" in result.output


def test_clear_cmd_aborted_keeps_history(runner, store):
    _make_snapshot(store, "dev")
    result = runner.invoke(history_group, ["clear", "dev"], input="n")
    assert result.exit_code != 0 or "Aborted" in result.output
    from stashenv.history import list_snapshots
    assert len(list_snapshots(store, "dev")) == 1
