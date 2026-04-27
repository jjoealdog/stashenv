import pytest
from click.testing import CliRunner
from pathlib import Path
from unittest.mock import patch
from stashenv.cli_lock import lock_group


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def store(tmp_path):
    with patch("stashenv.cli_lock._store_dir", return_value=tmp_path):
        yield tmp_path


def test_lock_cmd_locks_profile(runner, store):
    result = runner.invoke(lock_group, ["add", "prod"])
    assert result.exit_code == 0
    assert "locked" in result.output


def test_lock_cmd_already_locked_message(runner, store):
    runner.invoke(lock_group, ["add", "prod"])
    result = runner.invoke(lock_group, ["add", "prod"])
    assert result.exit_code == 0
    assert "already locked" in result.output


def test_unlock_cmd_unlocks_profile(runner, store):
    runner.invoke(lock_group, ["add", "prod"])
    result = runner.invoke(lock_group, ["remove", "prod"])
    assert result.exit_code == 0
    assert "unlocked" in result.output


def test_unlock_cmd_not_locked_message(runner, store):
    result = runner.invoke(lock_group, ["remove", "dev"])
    assert result.exit_code == 0
    assert "not locked" in result.output


def test_list_cmd_empty(runner, store):
    result = runner.invoke(lock_group, ["list"])
    assert result.exit_code == 0
    assert "No profiles" in result.output


def test_list_cmd_shows_locked_profiles(runner, store):
    runner.invoke(lock_group, ["add", "prod"])
    runner.invoke(lock_group, ["add", "staging"])
    result = runner.invoke(lock_group, ["list"])
    assert result.exit_code == 0
    assert "prod" in result.output
    assert "staging" in result.output
