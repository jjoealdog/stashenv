"""Tests for the export/import CLI commands."""

import json
import pytest
from pathlib import Path
from click.testing import CliRunner

from stashenv.cli_export import export_group
from stashenv.store import save_profile


PASSWORD = "s3cr3t"
PROJECT = "webapp"
PROFILE = "dev"
ENV_BYTES = b"API_KEY=abc123\nPORT=8080\n"


@pytest.fixture()
def runner():
    return CliRunner()


@pytest.fixture()
def store(tmp_path, monkeypatch):
    monkeypatch.setenv("STASHENV_DIR", str(tmp_path / "store"))
    save_profile(PROJECT, PROFILE, ENV_BYTES, PASSWORD)
    return tmp_path


def test_export_cmd_creates_file(runner, store, tmp_path):
    bundle_dir = str(tmp_path / "out")
    result = runner.invoke(export_group, ["export", PROJECT, PROFILE, "--dest", bundle_dir])
    assert result.exit_code == 0
    assert "Exported to" in result.output
    files = list(Path(bundle_dir).glob("*.stashenv"))
    assert len(files) == 1


def test_export_cmd_missing_profile_exits_nonzero(runner, store, tmp_path):
    result = runner.invoke(export_group, ["export", PROJECT, "ghost", "--dest", str(tmp_path)])
    assert result.exit_code != 0


def test_export_all_cmd(runner, store, tmp_path, monkeypatch):
    monkeypatch.setenv("STASHENV_DIR", str(store / "store"))
    save_profile(PROJECT, "staging", b"ENV=staging\n", PASSWORD)
    bundle_dir = str(tmp_path / "all_out")
    result = runner.invoke(export_group, ["export-all", PROJECT, "--dest", bundle_dir])
    assert result.exit_code == 0
    assert result.output.count("Exported") == 2


def test_export_all_cmd_no_profiles_exits_nonzero(runner, tmp_path, monkeypatch):
    monkeypatch.setenv("STASHENV_DIR", str(tmp_path / "empty"))
    result = runner.invoke(export_group, ["export-all", "noproject", "--dest", str(tmp_path)])
    assert result.exit_code != 0


def test_import_cmd_roundtrip(runner, store, tmp_path, monkeypatch):
    bundle_dir = tmp_path / "bundles"
    # Export first
    runner.invoke(export_group, ["export", PROJECT, PROFILE, "--dest", str(bundle_dir)])
    bundle_file = next(bundle_dir.glob("*.stashenv"))

    # Switch to a fresh store
    fresh = tmp_path / "fresh_store"
    monkeypatch.setenv("STASHENV_DIR", str(fresh))

    result = runner.invoke(export_group, ["import", str(bundle_file)])
    assert result.exit_code == 0
    assert "Imported profile" in result.output
    assert PROFILE in result.output


def test_import_cmd_with_project_override(runner, store, tmp_path, monkeypatch):
    bundle_dir = tmp_path / "bundles"
    runner.invoke(export_group, ["export", PROJECT, PROFILE, "--dest", str(bundle_dir)])
    bundle_file = next(bundle_dir.glob("*.stashenv"))

    fresh = tmp_path / "fresh2"
    monkeypatch.setenv("STASHENV_DIR", str(fresh))

    result = runner.invoke(export_group, ["import", str(bundle_file), "--project", "newapp"])
    assert result.exit_code == 0
    assert "newapp" in result.output
