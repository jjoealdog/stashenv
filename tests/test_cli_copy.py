"""Tests for the CLI copy commands."""

import pytest
from click.testing import CliRunner
from pathlib import Path
from stashenv.cli_copy import copy_group
from stashenv.store import save_profile, list_profiles


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def store(tmp_path):
    save_profile(tmp_path, "prod", b"KEY=prod_value", "mypassword")
    save_profile(tmp_path, "dev", b"KEY=dev_value", "devpass")
    return tmp_path


def test_copy_cmd_creates_destination(runner, store):
    result = runner.invoke(
        copy_group, ["profile", "prod", "prod-backup", "--store", str(store)]
    )
    assert result.exit_code == 0
    assert "prod-backup" in list_profiles(store)


def test_copy_cmd_success_message(runner, store):
    result = runner.invoke(
        copy_group, ["profile", "prod", "prod-backup", "--store", str(store)]
    )
    assert "copied" in result.output
    assert "prod" in result.output
    assert "prod-backup" in result.output


def test_copy_cmd_missing_source_exits_nonzero(runner, store):
    result = runner.invoke(
        copy_group, ["profile", "ghost", "ghost-copy", "--store", str(store)]
    )
    assert result.exit_code != 0


def test_copy_cmd_destination_exists_exits_nonzero(runner, store):
    result = runner.invoke(
        copy_group, ["profile", "prod", "dev", "--store", str(store)]
    )
    assert result.exit_code != 0


def test_copy_cmd_original_unchanged(runner, store):
    runner.invoke(
        copy_group, ["profile", "prod", "prod-backup", "--store", str(store)]
    )
    profiles = list_profiles(store)
    assert "prod" in profiles
    assert "dev" in profiles
