"""Tests for stashenv.env_patch."""
from pathlib import Path

import pytest

from stashenv.store import save_profile, load_profile
from stashenv.env_patch import patch_profile, PatchResult, ProfileNotFoundError


PASSWORD = "hunter2"


@pytest.fixture()
def store(tmp_path: Path) -> Path:
    env_text = "DB_HOST=localhost\nDB_PORT=5432\nDEBUG=true\n"
    save_profile(tmp_path, "dev", env_text, PASSWORD)
    return tmp_path


def test_patch_adds_new_key(store: Path) -> None:
    result = patch_profile(store, "dev", PASSWORD, set_keys={"NEW_KEY": "hello"})
    assert "NEW_KEY" in result.added
    assert result.updated == []
    text = load_profile(store, "dev", PASSWORD)
    assert "NEW_KEY=hello" in text


def test_patch_updates_existing_key(store: Path) -> None:
    result = patch_profile(store, "dev", PASSWORD, set_keys={"DB_PORT": "3306"})
    assert "DB_PORT" in result.updated
    assert result.added == []
    text = load_profile(store, "dev", PASSWORD)
    assert "DB_PORT=3306" in text


def test_patch_removes_key(store: Path) -> None:
    result = patch_profile(store, "dev", PASSWORD, remove_keys=["DEBUG"])
    assert "DEBUG" in result.removed
    text = load_profile(store, "dev", PASSWORD)
    assert "DEBUG" not in text


def test_patch_remove_nonexistent_key_is_silent(store: Path) -> None:
    result = patch_profile(store, "dev", PASSWORD, remove_keys=["DOES_NOT_EXIST"])
    assert result.removed == []


def test_patch_combined_set_and_remove(store: Path) -> None:
    result = patch_profile(
        store,
        "dev",
        PASSWORD,
        set_keys={"API_KEY": "secret"},
        remove_keys=["DEBUG"],
    )
    assert "API_KEY" in result.added
    assert "DEBUG" in result.removed
    text = load_profile(store, "dev", PASSWORD)
    assert "API_KEY=secret" in text
    assert "DEBUG" not in text


def test_patch_missing_profile_raises(store: Path) -> None:
    with pytest.raises(ProfileNotFoundError):
        patch_profile(store, "ghost", PASSWORD, set_keys={"X": "1"})


def test_patch_no_change_to_same_value_not_in_updated(store: Path) -> None:
    result = patch_profile(store, "dev", PASSWORD, set_keys={"DB_HOST": "localhost"})
    # value unchanged — should not appear in updated
    assert "DB_HOST" not in result.updated
    assert "DB_HOST" not in result.added


def test_patch_result_total_changes(store: Path) -> None:
    result = PatchResult(added=["A"], updated=["B", "C"], removed=["D"])
    assert result.total_changes == 4
