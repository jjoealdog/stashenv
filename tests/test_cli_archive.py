"""Tests for stashenv.cli_archive."""

import pytest
from pathlib import Path
from click.testing import CliRunner

from stashenv.store import save_profile, load_profile
from stashenv.cli_archive import archive_group


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def store(tmp_path):
    d = tmp_path / "store"
    d.mkdir()
    save_profile(d, "dev", b"KEY=dev\nFOO=bar", "secret")
    save_profile(d, "prod", b"KEY=prod\nFOO=baz", "secret")
    return d


def _obj(store_dir: Path) -> dict:
    return {"project_dir": store_dir.parent}


def test_create_cmd_creates_file(runner, store, tmp_path):
    out = str(tmp_path / "backup.tar.gz")
    result = runner.invoke(
        archive_group, ["create", out], obj=_obj(store)
    )
    assert result.exit_code == 0
    assert Path(out).exists()


def test_create_cmd_shows_profile_names(runner, store, tmp_path):
    out = str(tmp_path / "backup.tar.gz")
    result = runner.invoke(
        archive_group, ["create", out], obj=_obj(store)
    )
    assert "dev" in result.output
    assert "prod" in result.output


def test_create_cmd_subset_of_profiles(runner, store, tmp_path):
    out = str(tmp_path / "partial.tar.gz")
    result = runner.invoke(
        archive_group,
        ["create", out, "--profile", "dev"],
        obj=_obj(store),
    )
    assert result.exit_code == 0
    assert "dev" in result.output
    assert "prod" not in result.output


def test_create_cmd_missing_profile_exits_nonzero(runner, store, tmp_path):
    out = str(tmp_path / "bad.tar.gz")
    result = runner.invoke(
        archive_group,
        ["create", out, "--profile", "ghost"],
        obj=_obj(store),
    )
    assert result.exit_code != 0
    assert "Error" in result.output


def test_restore_cmd_restores_profiles(runner, store, tmp_path):
    out = str(tmp_path / "backup.tar.gz")
    runner.invoke(archive_group, ["create", out], obj=_obj(store))

    new_store = tmp_path / "new_store"
    new_store.mkdir()
    result = runner.invoke(
        archive_group, ["restore", out], obj={"project_dir": new_store.parent}
    )
    assert result.exit_code == 0
    assert "Restored" in result.output


def test_restore_cmd_conflict_exits_nonzero(runner, store, tmp_path):
    out = str(tmp_path / "backup.tar.gz")
    runner.invoke(archive_group, ["create", out], obj=_obj(store))
    # restore into the same store without --overwrite
    result = runner.invoke(
        archive_group, ["restore", out], obj=_obj(store)
    )
    assert result.exit_code != 0
    assert "Error" in result.output


def test_restore_cmd_overwrite_flag(runner, store, tmp_path):
    out = str(tmp_path / "backup.tar.gz")
    runner.invoke(archive_group, ["create", out], obj=_obj(store))
    result = runner.invoke(
        archive_group, ["restore", out, "--overwrite"], obj=_obj(store)
    )
    assert result.exit_code == 0
