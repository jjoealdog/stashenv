"""Tests for stashenv.env_split."""

import pytest
from pathlib import Path

from stashenv.store import save_profile, load_profile
from stashenv.env_split import (
    split_profile,
    SplitResult,
    ProfileNotFoundError,
    SplitError,
)

PASSWORD = "test-pass"


@pytest.fixture()
def store(tmp_path: Path) -> Path:
    content = "DB_HOST=localhost\nDB_PORT=5432\nAPP_KEY=abc123\nAPP_SECRET=xyz789\nDEBUG=true\n"
    save_profile(tmp_path, "full", content, PASSWORD)
    return tmp_path


def test_split_creates_destination_profiles(store: Path):
    split_profile(
        store,
        "full",
        PASSWORD,
        {"db": ["DB_HOST", "DB_PORT"], "app": ["APP_KEY", "APP_SECRET"]},
    )
    assert (store / "db.env.enc").exists()
    assert (store / "app.env.enc").exists()


def test_split_destination_contains_correct_keys(store: Path):
    split_profile(
        store,
        "full",
        PASSWORD,
        {"db": ["DB_HOST", "DB_PORT"]},
    )
    text = load_profile(store, "db", PASSWORD)
    assert "DB_HOST=localhost" in text
    assert "DB_PORT=5432" in text
    assert "APP_KEY" not in text


def test_split_result_tracks_destinations(store: Path):
    result = split_profile(
        store,
        "full",
        PASSWORD,
        {"db": ["DB_HOST", "DB_PORT"], "app": ["APP_KEY", "APP_SECRET"]},
    )
    assert set(result.destinations) == {"db", "app"}


def test_split_result_counts_keys(store: Path):
    result = split_profile(
        store,
        "full",
        PASSWORD,
        {"db": ["DB_HOST", "DB_PORT"]},
    )
    assert result.total_keys == 5
    assert result.keys_placed == 2
    assert result.unplaced == 3


def test_split_remainder_profile_captures_unplaced_keys(store: Path):
    split_profile(
        store,
        "full",
        PASSWORD,
        {"db": ["DB_HOST", "DB_PORT"]},
        remainder_profile="misc",
    )
    text = load_profile(store, "misc", PASSWORD)
    assert "APP_KEY" in text
    assert "DEBUG" in text
    assert "DB_HOST" not in text


def test_split_missing_source_raises(store: Path):
    with pytest.raises(ProfileNotFoundError):
        split_profile(store, "nonexistent", PASSWORD, {"db": ["DB_HOST"]})


def test_split_existing_destination_raises_without_overwrite(store: Path):
    save_profile(store, "db", "DB_HOST=other", PASSWORD)
    with pytest.raises(SplitError, match="already exists"):
        split_profile(store, "full", PASSWORD, {"db": ["DB_HOST", "DB_PORT"]})


def test_split_overwrite_flag_replaces_existing(store: Path):
    save_profile(store, "db", "DB_HOST=other", PASSWORD)
    split_profile(
        store, "full", PASSWORD, {"db": ["DB_HOST", "DB_PORT"]}, overwrite=True
    )
    text = load_profile(store, "db", PASSWORD)
    assert "DB_HOST=localhost" in text


def test_split_ignores_missing_keys_in_group(store: Path):
    result = split_profile(
        store,
        "full",
        PASSWORD,
        {"db": ["DB_HOST", "NONEXISTENT_KEY"]},
    )
    text = load_profile(store, "db", PASSWORD)
    assert "DB_HOST=localhost" in text
    assert "NONEXISTENT_KEY" not in text
