"""Tests for snapshot_diff module and CLI."""

import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock
from click.testing import CliRunner

from stashenv.snapshot_diff import (
    diff_against_snapshot,
    format_snapshot_diff,
    SnapshotNotFoundError,
    ProfileNotFoundError,
)
from stashenv.diff import DiffEntry
from stashenv.cli_snapshot_diff import snapshot_diff_group


@pytest.fixture
def store_dir(tmp_path):
    return tmp_path


@pytest.fixture
def runner():
    return CliRunner()


def _make_entries():
    return [
        DiffEntry(key="FOO", status="changed", old_value="bar", new_value="baz"),
        DiffEntry(key="NEW_KEY", status="added", old_value=None, new_value="hello"),
    ]


def test_diff_against_snapshot_raises_when_snapshot_missing(store_dir):
    with patch("stashenv.snapshot_diff.list_snapshots", return_value=[]):
        with pytest.raises(SnapshotNotFoundError):
            diff_against_snapshot(store_dir, "dev", "pass", version=99)


def test_diff_against_snapshot_raises_when_profile_missing(store_dir):
    with patch("stashenv.snapshot_diff.list_snapshots", return_value=[{"version": 1}]):
        with patch("stashenv.snapshot_diff.get_snapshot", return_value=b"FOO=bar\n"):
            with patch("stashenv.snapshot_diff.load_profile", side_effect=FileNotFoundError):
                with pytest.raises(ProfileNotFoundError):
                    diff_against_snapshot(store_dir, "dev", "pass", version=1)


def test_diff_against_snapshot_returns_diff_entries(store_dir):
    with patch("stashenv.snapshot_diff.list_snapshots", return_value=[{"version": 1}]):
        with patch("stashenv.snapshot_diff.get_snapshot", return_value=b"FOO=bar\n"):
            with patch("stashenv.snapshot_diff.load_profile", return_value="FOO=baz\nNEW=x\n"):
                entries = diff_against_snapshot(store_dir, "dev", "pass", version=1)
    keys = {e.key for e in entries}
    assert "FOO" in keys
    assert "NEW" in keys


def test_format_snapshot_diff_includes_header():
    entries = _make_entries()
    result = format_snapshot_diff(entries, "dev", 2)
    assert "--- dev @ v2" in result
    assert "+++ dev (current)" in result


def test_format_snapshot_diff_no_differences_message():
    result = format_snapshot_diff([], "dev", 1)
    assert "(no differences)" in result


def test_show_cmd_success(runner):
    entries = _make_entries()
    with patch("stashenv.cli_snapshot_diff._store_dir", return_value=Path("/tmp")):
        with patch("stashenv.cli_snapshot_diff.diff_against_snapshot", return_value=entries):
            result = runner.invoke(
                snapshot_diff_group,
                ["show", "dev", "1", "--password", "secret"],
            )
    assert result.exit_code == 0
    assert "dev" in result.output


def test_show_cmd_missing_snapshot_exits_nonzero(runner):
    with patch("stashenv.cli_snapshot_diff._store_dir", return_value=Path("/tmp")):
        with patch(
            "stashenv.cli_snapshot_diff.diff_against_snapshot",
            side_effect=SnapshotNotFoundError("not found"),
        ):
            result = runner.invoke(
                snapshot_diff_group,
                ["show", "dev", "99", "--password", "secret"],
            )
    assert result.exit_code != 0


def test_show_cmd_missing_profile_exits_nonzero(runner):
    with patch("stashenv.cli_snapshot_diff._store_dir", return_value=Path("/tmp")):
        with patch(
            "stashenv.cli_snapshot_diff.diff_against_snapshot",
            side_effect=ProfileNotFoundError("no profile"),
        ):
            result = runner.invoke(
                snapshot_diff_group,
                ["show", "ghost", "1", "--password", "secret"],
            )
    assert result.exit_code != 0
