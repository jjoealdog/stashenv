"""Tests for the diff CLI commands."""

from __future__ import annotations

import os
import pytest
from click.testing import CliRunner

from stashenv.cli_diff import diff_group
from stashenv.store import save_profile


PASSWORD = "testpass"

ENV_A = "DB_HOST=localhost\nDB_PORT=5432\nSECRET=abc\n"
ENV_B = "DB_HOST=prod.example.com\nDB_PORT=5432\nNEW_VAR=hello\n"


@pytest.fixture()
def runner(tmp_path, monkeypatch):
    monkeypatch.setenv("STASHENV_DIR", str(tmp_path))
    return CliRunner()


@pytest.fixture()
def store(tmp_path, monkeypatch):
    monkeypatch.setenv("STASHENV_DIR", str(tmp_path))
    save_profile("alpha", ENV_A, PASSWORD)
    save_profile("beta", ENV_B, PASSWORD)


def test_diff_cmd_shows_differences(runner, store):
    result = runner.invoke(
        diff_group,
        ["profiles", "alpha", "beta", "--password", PASSWORD],
    )
    assert result.exit_code == 0
    assert "+" in result.output
    assert "-" in result.output


def test_diff_cmd_shows_header(runner, store):
    result = runner.invoke(
        diff_group,
        ["profiles", "alpha", "beta", "--password", PASSWORD],
    )
    assert "--- alpha" in result.output
    assert "+++ beta" in result.output


def test_diff_cmd_show_values(runner, store):
    result = runner.invoke(
        diff_group,
        ["profiles", "alpha", "beta", "--password", PASSWORD, "--show-values"],
    )
    assert result.exit_code == 0
    assert "->" in result.output


def test_diff_cmd_filter_only_added(runner, store):
    result = runner.invoke(
        diff_group,
        ["profiles", "alpha", "beta", "--password", PASSWORD, "--only", "added"],
    )
    assert result.exit_code == 0
    assert "NEW_VAR" in result.output
    assert "SECRET" not in result.output


def test_diff_cmd_missing_profile_exits_nonzero(runner, store):
    result = runner.invoke(
        diff_group,
        ["profiles", "alpha", "ghost", "--password", PASSWORD],
    )
    assert result.exit_code != 0


def test_diff_cmd_wrong_password_exits_nonzero(runner, store):
    result = runner.invoke(
        diff_group,
        ["profiles", "alpha", "beta", "--password", "wrongpass"],
    )
    assert result.exit_code != 0


def test_diff_cmd_identical_profiles(runner, tmp_path, monkeypatch):
    monkeypatch.setenv("STASHENV_DIR", str(tmp_path))
    save_profile("x", ENV_A, PASSWORD)
    save_profile("y", ENV_A, PASSWORD)
    result = runner.invoke(
        diff_group,
        ["profiles", "x", "y", "--password", PASSWORD],
    )
    assert result.exit_code == 0
    assert "No differences" in result.output
