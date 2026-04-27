"""Tests for the audit CLI commands."""

import pytest
from click.testing import CliRunner
from pathlib import Path
from unittest.mock import patch

from stashenv.cli_audit import audit_group
from stashenv.audit import record_event


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def store(tmp_path):
    store_dir = tmp_path / "store"
    store_dir.mkdir()
    return store_dir


def test_log_cmd_empty(runner, store):
    with patch("stashenv.cli_audit._store_dir", return_value=store):
        result = runner.invoke(audit_group, ["log"])
    assert result.exit_code == 0
    assert "No audit events found" in result.output


def test_log_cmd_shows_events(runner, store):
    record_event(store, "save", "prod")
    record_event(store, "load", "dev")
    with patch("stashenv.cli_audit._store_dir", return_value=store):
        result = runner.invoke(audit_group, ["log"])
    assert result.exit_code == 0
    assert "save" in result.output
    assert "load" in result.output


def test_log_cmd_filter_by_profile(runner, store):
    record_event(store, "save", "prod")
    record_event(store, "load", "dev")
    with patch("stashenv.cli_audit._store_dir", return_value=store):
        result = runner.invoke(audit_group, ["log", "--profile", "prod"])
    assert "prod" in result.output
    assert "dev" not in result.output


def test_log_cmd_filter_by_action(runner, store):
    record_event(store, "save", "prod")
    record_event(store, "load", "prod")
    with patch("stashenv.cli_audit._store_dir", return_value=store):
        result = runner.invoke(audit_group, ["log", "--action", "save"])
    assert "save" in result.output
    assert "load" not in result.output


def test_log_cmd_last_n(runner, store):
    for i in range(5):
        record_event(store, "load", f"profile{i}")
    with patch("stashenv.cli_audit._store_dir", return_value=store):
        result = runner.invoke(audit_group, ["log", "--last", "2"])
    lines = [l for l in result.output.strip().splitlines() if l]
    assert len(lines) == 2


def test_clear_cmd(runner, store):
    record_event(store, "save", "prod")
    with patch("stashenv.cli_audit._store_dir", return_value=store):
        result = runner.invoke(audit_group, ["clear"], input="y\n")
    assert result.exit_code == 0
    assert "cleared" in result.output
    assert not (store / ".audit.log").exists()
