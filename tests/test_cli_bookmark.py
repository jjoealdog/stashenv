"""Tests for stashenv.cli_bookmark."""

import pytest
from click.testing import CliRunner
from pathlib import Path
from unittest.mock import patch

from stashenv.cli_bookmark import bookmark_group


@pytest.fixture()
def runner():
    return CliRunner()


@pytest.fixture()
def store(tmp_path: Path):
    with patch("stashenv.cli_bookmark._store_dir", return_value=tmp_path):
        yield tmp_path


def test_add_cmd_creates_bookmark(runner, store):
    result = runner.invoke(bookmark_group, ["add", "prod", "production"])
    assert result.exit_code == 0
    assert "prod" in result.output


def test_add_cmd_duplicate_exits_nonzero(runner, store):
    runner.invoke(bookmark_group, ["add", "prod", "production"])
    result = runner.invoke(bookmark_group, ["add", "prod", "other"])
    assert result.exit_code != 0
    assert "already exists" in result.output


def test_add_cmd_overwrite_flag(runner, store):
    runner.invoke(bookmark_group, ["add", "prod", "production"])
    result = runner.invoke(bookmark_group, ["add", "--overwrite", "prod", "staging"])
    assert result.exit_code == 0
    resolve = runner.invoke(bookmark_group, ["resolve", "prod"])
    assert "staging" in resolve.output


def test_resolve_cmd_shows_profile(runner, store):
    runner.invoke(bookmark_group, ["add", "dev", "development"])
    result = runner.invoke(bookmark_group, ["resolve", "dev"])
    assert result.exit_code == 0
    assert "development" in result.output


def test_resolve_cmd_missing_exits_nonzero(runner, store):
    result = runner.invoke(bookmark_group, ["resolve", "nope"])
    assert result.exit_code != 0


def test_remove_cmd_removes_bookmark(runner, store):
    runner.invoke(bookmark_group, ["add", "prod", "production"])
    result = runner.invoke(bookmark_group, ["remove", "prod"])
    assert result.exit_code == 0
    resolve = runner.invoke(bookmark_group, ["resolve", "prod"])
    assert resolve.exit_code != 0


def test_remove_cmd_missing_exits_nonzero(runner, store):
    result = runner.invoke(bookmark_group, ["remove", "ghost"])
    assert result.exit_code != 0


def test_list_cmd_empty_message(runner, store):
    result = runner.invoke(bookmark_group, ["list"])
    assert result.exit_code == 0
    assert "No bookmarks" in result.output


def test_list_cmd_shows_all_bookmarks(runner, store):
    runner.invoke(bookmark_group, ["add", "prod", "production"])
    runner.invoke(bookmark_group, ["add", "dev", "development"])
    result = runner.invoke(bookmark_group, ["list"])
    assert "prod" in result.output
    assert "dev" in result.output
