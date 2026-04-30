"""Tests for stashenv.cli_lint."""
import pytest
from click.testing import CliRunner
from pathlib import Path

from stashenv.cli_lint import lint_group
from stashenv.store import save_profile


GOOD_ENV = "DB_HOST=localhost\nDB_PORT=5432\n"
BAD_ENV = "NO_EQUALS\nFOO=\n"


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def store(tmp_path):
    return tmp_path


def _invoke(runner, store, *args):
    return runner.invoke(lint_group, args, obj={"store_dir": store})


def test_run_cmd_clean_profile_exits_zero(runner, store):
    save_profile(store, "prod", GOOD_ENV, "pw")
    result = _invoke(runner, store, "run", "prod", "--password", "pw")
    assert result.exit_code == 0
    assert "no issues" in result.output


def test_run_cmd_bad_profile_exits_nonzero(runner, store):
    save_profile(store, "dev", BAD_ENV, "pw")
    result = _invoke(runner, store, "run", "dev", "--password", "pw")
    assert result.exit_code != 0


def test_run_cmd_missing_profile_exits_nonzero(runner, store):
    result = _invoke(runner, store, "run", "ghost", "--password", "pw")
    assert result.exit_code != 0
    assert "not found" in result.output


def test_run_cmd_shows_line_number(runner, store):
    save_profile(store, "dev", "FIRST=ok\nBADLINE\n", "pw")
    result = _invoke(runner, store, "run", "dev", "--password", "pw")
    assert "line" in result.output
    assert "2" in result.output


def test_all_cmd_no_profiles(runner, store):
    result = _invoke(runner, store, "all", "--password", "pw")
    assert result.exit_code == 0
    assert "No profiles" in result.output


def test_all_cmd_all_clean_exits_zero(runner, store):
    save_profile(store, "a", GOOD_ENV, "pw")
    save_profile(store, "b", GOOD_ENV, "pw")
    result = _invoke(runner, store, "all", "--password", "pw")
    assert result.exit_code == 0


def test_all_cmd_one_bad_exits_nonzero(runner, store):
    save_profile(store, "good", GOOD_ENV, "pw")
    save_profile(store, "bad", BAD_ENV, "pw")
    result = _invoke(runner, store, "all", "--password", "pw")
    assert result.exit_code != 0
