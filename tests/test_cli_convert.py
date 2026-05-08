"""Tests for stashenv.cli_convert."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from click.testing import CliRunner

from stashenv.cli_convert import convert_group
from stashenv.store import save_profile, _store_dir


@pytest.fixture()
def runner():
    return CliRunner()


@pytest.fixture()
def store(tmp_path, monkeypatch):
    store_dir = tmp_path / ".stashenv"
    store_dir.mkdir()
    monkeypatch.setattr("stashenv.cli_convert._store_dir", lambda: store_dir)
    env_text = "API_KEY=secret\nBASE_URL=https://example.com\n"
    save_profile(store_dir, "prod", "hunter2", env_text)
    return store_dir


def test_export_cmd_dotenv_to_stdout(runner, store):
    result = runner.invoke(convert_group, ["export", "prod", "--password", "hunter2", "--format", "dotenv"])
    assert result.exit_code == 0
    assert "API_KEY=secret" in result.output


def test_export_cmd_json_to_stdout(runner, store):
    result = runner.invoke(convert_group, ["export", "prod", "--password", "hunter2", "--format", "json"])
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert data["API_KEY"] == "secret"


def test_export_cmd_yaml_to_stdout(runner, store):
    result = runner.invoke(convert_group, ["export", "prod", "--password", "hunter2", "--format", "yaml"])
    assert result.exit_code == 0
    assert "API_KEY: secret" in result.output


def test_export_cmd_writes_file(runner, store, tmp_path):
    out_file = tmp_path / "out.json"
    result = runner.invoke(
        convert_group,
        ["export", "prod", "--password", "hunter2", "--format", "json", "--output", str(out_file)],
    )
    assert result.exit_code == 0
    assert out_file.exists()
    data = json.loads(out_file.read_text())
    assert "API_KEY" in data


def test_export_cmd_missing_profile_exits_nonzero(runner, store):
    result = runner.invoke(convert_group, ["export", "ghost", "--password", "x"])
    assert result.exit_code != 0


def test_import_cmd_dotenv(runner, store, tmp_path):
    env_file = tmp_path / "new.env"
    env_file.write_text("IMPORTED_KEY=yes\nFOO=bar\n")
    result = runner.invoke(
        convert_group,
        ["import", "newprofile", str(env_file), "--password", "abc", "--format", "dotenv"],
        input="abc\n",
    )
    assert result.exit_code == 0
    assert "newprofile" in result.output


def test_import_cmd_json(runner, store, tmp_path):
    json_file = tmp_path / "data.json"
    json_file.write_text(json.dumps({"X": "1", "Y": "2"}))
    result = runner.invoke(
        convert_group,
        ["import", "fromjson", str(json_file), "--password", "pw", "--format", "json"],
        input="pw\n",
    )
    assert result.exit_code == 0


def test_import_cmd_missing_file_exits_nonzero(runner, store):
    result = runner.invoke(
        convert_group,
        ["import", "x", "/nonexistent/file.env", "--password", "pw"],
    )
    assert result.exit_code != 0
