"""Tests for CLI rotate commands."""

import pytest
from click.testing import CliRunner
from pathlib import Path
from stashenv.cli_rotate import rotate_group
from stashenv.store import save_profile, load_profile, _store_dir


@pytest.fixture
def runner() -> CliRunner:
    return CliRunner()


@pytest.fixture
def store(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    store_dir = tmp_path / "store"
    monkeypatch.setattr("stashenv.cli_rotate._store_dir", lambda: store_dir)
    monkeypatch.setattr("stashenv.rotate._profile_path",
        lambda name, d=None: (store_dir / name).with_suffix(".env.enc"))
    return store_dir


def test_rotate_cmd_success(runner: CliRunner, store: Path) -> None:
    save_profile("dev", b"KEY=val", "oldpass", store)
    result = runner.invoke(
        rotate_group,
        ["profile", "dev"],
        input="oldpass\nnewpass\nnewpass\n",
    )
    assert result.exit_code == 0
    assert "rotated" in result.output.lower()


def test_rotate_cmd_missing_profile_exits_nonzero(runner: CliRunner, store: Path) -> None:
    result = runner.invoke(
        rotate_group,
        ["profile", "ghost"],
        input="oldpass\nnewpass\nnewpass\n",
    )
    assert result.exit_code != 0


def test_rotate_cmd_wrong_password_exits_nonzero(runner: CliRunner, store: Path) -> None:
    save_profile("dev", b"KEY=val", "correct", store)
    result = runner.invoke(
        rotate_group,
        ["profile", "dev"],
        input="wrong\nnewpass\nnewpass\n",
    )
    assert result.exit_code != 0


def test_rotate_all_cmd_no_profiles(runner: CliRunner, store: Path) -> None:
    result = runner.invoke(
        rotate_group,
        ["all"],
        input="oldpass\nnewpass\nnewpass\n",
    )
    assert result.exit_code == 0
    assert "No profiles" in result.output


def test_rotate_all_cmd_reports_rotated(runner: CliRunner, store: Path) -> None:
    save_profile("dev", b"A=1", "pass", store)
    save_profile("prod", b"B=2", "pass", store)
    result = runner.invoke(
        rotate_group,
        ["all"],
        input="pass\nnewpass\nnewpass\n",
    )
    assert result.exit_code == 0
    assert "dev" in result.output
    assert "prod" in result.output
