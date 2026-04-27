"""Tests for stashenv/history.py"""

import pytest
from pathlib import Path
from stashenv.history import (
    snapshot_profile,
    list_snapshots,
    get_snapshot,
    clear_history,
)


@pytest.fixture
def store_dir(tmp_path):
    return tmp_path


FAKE_DATA_V1 = b"encrypted-blob-version-1"
FAKE_DATA_V2 = b"encrypted-blob-version-2"


def test_snapshot_returns_version_number(store_dir):
    v = snapshot_profile(store_dir, "dev", FAKE_DATA_V1)
    assert v == 1


def test_snapshot_increments_version(store_dir):
    snapshot_profile(store_dir, "dev", FAKE_DATA_V1)
    v = snapshot_profile(store_dir, "dev", FAKE_DATA_V2)
    assert v == 2


def test_snapshot_creates_bin_file(store_dir):
    snapshot_profile(store_dir, "dev", FAKE_DATA_V1)
    snap_file = store_dir / ".history" / "dev" / "v1.bin"
    assert snap_file.exists()
    assert snap_file.read_bytes() == FAKE_DATA_V1


def test_list_snapshots_empty_when_no_history(store_dir):
    assert list_snapshots(store_dir, "dev") == []


def test_list_snapshots_newest_first(store_dir):
    snapshot_profile(store_dir, "dev", FAKE_DATA_V1, note="first")
    snapshot_profile(store_dir, "dev", FAKE_DATA_V2, note="second")
    snaps = list_snapshots(store_dir, "dev")
    assert snaps[0]["version"] == 2
    assert snaps[1]["version"] == 1


def test_list_snapshots_includes_note(store_dir):
    snapshot_profile(store_dir, "dev", FAKE_DATA_V1, note="before migration")
    snaps = list_snapshots(store_dir, "dev")
    assert snaps[0]["note"] == "before migration"


def test_get_snapshot_returns_correct_bytes(store_dir):
    snapshot_profile(store_dir, "dev", FAKE_DATA_V1)
    snapshot_profile(store_dir, "dev", FAKE_DATA_V2)
    assert get_snapshot(store_dir, "dev", 1) == FAKE_DATA_V1
    assert get_snapshot(store_dir, "dev", 2) == FAKE_DATA_V2


def test_get_snapshot_missing_version_returns_none(store_dir):
    assert get_snapshot(store_dir, "dev", 99) is None


def test_clear_history_removes_files(store_dir):
    snapshot_profile(store_dir, "dev", FAKE_DATA_V1)
    snapshot_profile(store_dir, "dev", FAKE_DATA_V2)
    removed = clear_history(store_dir, "dev")
    assert removed == 2
    assert list_snapshots(store_dir, "dev") == []


def test_snapshots_are_isolated_per_profile(store_dir):
    snapshot_profile(store_dir, "dev", FAKE_DATA_V1)
    snapshot_profile(store_dir, "prod", FAKE_DATA_V2)
    assert len(list_snapshots(store_dir, "dev")) == 1
    assert len(list_snapshots(store_dir, "prod")) == 1
    assert get_snapshot(store_dir, "dev", 1) == FAKE_DATA_V1
    assert get_snapshot(store_dir, "prod", 1) == FAKE_DATA_V2
