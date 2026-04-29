"""Tests for stashenv.cli_alias."""

import pytest
from click.testing import CliRunner
from pathlib import Path

from stashenv.cli_alias import alias_group
from stashenv.alias import set_alias


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def store(tmp_path: Path, monkeypatch):
    store_dir = tmp_path / ".stashenv"
    store_dir.mkdir()
    monkeypatch.setattr("stashenv.cli_alias._store_dir", lambda: store_dir)
    return store_dir


def test_set_cmd_creates_alias(runner, store):
    result = runner.invoke(alias_group, ["set", "prod", "production"])
    assert result.exit_code == 0
    assert "prod" in result.output
    assert "production" in result.output


def test_set_cmd_duplicate_exits_nonzero(runner, store):
    set_alias(store, "prod", "production")
    result = runner.invoke(alias_group, ["set", "prod", "other"])
    assert result.exit_code != 0


def test_set_cmd_overwrite_flag(runner, store):
    set_alias(store, "prod", "production")
    result = runner.invoke(alias_group, ["set", "--overwrite", "prod", "production-v2"])
    assert result.exit_code == 0
    assert "production-v2" in result.output


def test_remove_cmd_removes_alias(runner, store):
    set_alias(store, "prod", "production")
    result = runner.invoke(alias_group, ["remove", "prod"])
    assert result.exit_code == 0
    assert "removed" in result.output


def test_remove_cmd_missing_alias_exits_nonzero(runner, store):
    result = runner.invoke(alias_group, ["remove", "ghost"])
    assert result.exit_code != 0


def test_resolve_cmd_prints_profile(runner, store):
    set_alias(store, "s", "staging")
    result = runner.invoke(alias_group, ["resolve", "s"])
    assert result.exit_code == 0
    assert "staging" in result.output


def test_resolve_cmd_missing_alias_exits_nonzero(runner, store):
    result = runner.invoke(alias_group, ["resolve", "nope"])
    assert result.exit_code != 0


def test_list_cmd_empty(runner, store):
    result = runner.invoke(alias_group, ["list"])
    assert result.exit_code == 0
    assert "No aliases" in result.output


def test_list_cmd_shows_all_aliases(runner, store):
    set_alias(store, "prod", "production")
    set_alias(store, "dev", "development")
    result = runner.invoke(alias_group, ["list"])
    assert result.exit_code == 0
    assert "prod" in result.output
    assert "dev" in result.output
