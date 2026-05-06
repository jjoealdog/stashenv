"""Tests for stashenv.cli_ttl."""

from __future__ import annotations

import json
import time
from pathlib import Path

import pytest
from click.testing import CliRunner

from stashenv.cli_ttl import ttl_group


@pytest.fixture()
def runner():
    return CliRunner()


@pytest.fixture()
def store(tmp_path, monkeypatch):
    monkeypatch.setenv("STASHENV_DIR", str(tmp_path))
    return tmp_path


def test_set_cmd_creates_ttl_entry(runner, store):
    result = runner.invoke(ttl_group, ["set", "dev", "3600"])
    assert result.exit_code == 0
    assert "TTL for 'dev' set to 3600s" in result.output
    assert (store / ".ttl.json").exists()


def test_set_cmd_rejects_non_positive_seconds(runner, store):
    result = runner.invoke(ttl_group, ["set", "dev", "0"])
    assert result.exit_code != 0


def test_get_cmd_shows_no_ttl_message(runner, store):
    result = runner.invoke(ttl_group, ["get", "dev"])
    assert result.exit_code == 0
    assert "No TTL set" in result.output


def test_get_cmd_shows_ttl_record(runner, store):
    runner.invoke(ttl_group, ["set", "dev", "3600"])
    result = runner.invoke(ttl_group, ["get", "dev"])
    assert result.exit_code == 0
    assert "ttl" in result.output
    assert "3600" in result.output


def test_get_cmd_shows_stale_marker(runner, store):
    runner.invoke(ttl_group, ["set", "dev", "1"])
    p = store / ".ttl.json"
    data = json.loads(p.read_text())
    data["dev"]["created_at"] = time.time() - 100
    p.write_text(json.dumps(data))
    result = runner.invoke(ttl_group, ["get", "dev"])
    assert "stale" in result.output


def test_clear_cmd_removes_entry(runner, store):
    runner.invoke(ttl_group, ["set", "dev", "3600"])
    result = runner.invoke(ttl_group, ["clear", "dev"])
    assert result.exit_code == 0
    assert "cleared" in result.output
    data = json.loads((store / ".ttl.json").read_text())
    assert "dev" not in data


def test_list_cmd_empty(runner, store):
    result = runner.invoke(ttl_group, ["list"])
    assert result.exit_code == 0
    assert "No TTL entries" in result.output


def test_list_cmd_shows_profiles(runner, store):
    runner.invoke(ttl_group, ["set", "dev", "3600"])
    runner.invoke(ttl_group, ["set", "prod", "7200"])
    result = runner.invoke(ttl_group, ["list"])
    assert result.exit_code == 0
    assert "dev" in result.output
    assert "prod" in result.output
