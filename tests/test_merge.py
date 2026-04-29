"""Tests for stashenv.merge."""
import pytest
from pathlib import Path

from stashenv.store import save_profile, load_profile
from stashenv.merge import (
    merge_profiles,
    ProfileNotFoundError,
    ProfileAlreadyExistsError,
)


@pytest.fixture()
def store(tmp_path: Path) -> Path:
    save_profile(tmp_path, "base", "KEY1=hello\nKEY2=world", "pass")
    save_profile(tmp_path, "override", "KEY2=OVERRIDE\nKEY3=extra", "pass")
    return tmp_path


def test_merge_creates_destination(store: Path) -> None:
    merge_profiles(store, "base", "override", "merged", "pass", "pass", "pass")
    profiles = [p.stem for p in store.iterdir() if p.suffix == ".env"]
    assert "merged" in profiles


def test_merge_override_strategy_prefers_override(store: Path) -> None:
    merge_profiles(store, "base", "override", "merged", "pass", "pass", "pass", strategy="override")
    text = load_profile(store, "merged", "pass")
    assert "KEY2=OVERRIDE" in text


def test_merge_base_strategy_prefers_base(store: Path) -> None:
    merge_profiles(store, "base", "override", "merged", "pass", "pass", "pass", strategy="base")
    text = load_profile(store, "merged", "pass")
    assert "KEY2=world" in text


def test_merge_includes_all_keys(store: Path) -> None:
    merge_profiles(store, "base", "override", "merged", "pass", "pass", "pass")
    text = load_profile(store, "merged", "pass")
    assert "KEY1=hello" in text
    assert "KEY3=extra" in text


def test_merge_returns_key_count(store: Path) -> None:
    count = merge_profiles(store, "base", "override", "merged", "pass", "pass", "pass")
    assert count == 3  # KEY1, KEY2, KEY3


def test_merge_missing_base_raises(store: Path) -> None:
    with pytest.raises(ProfileNotFoundError):
        merge_profiles(store, "ghost", "override", "merged", "pass", "pass", "pass")


def test_merge_missing_override_raises(store: Path) -> None:
    with pytest.raises(ProfileNotFoundError):
        merge_profiles(store, "base", "ghost", "merged", "pass", "pass", "pass")


def test_merge_existing_dest_raises_without_overwrite(store: Path) -> None:
    merge_profiles(store, "base", "override", "merged", "pass", "pass", "pass")
    with pytest.raises(ProfileAlreadyExistsError):
        merge_profiles(store, "base", "override", "merged", "pass", "pass", "pass")


def test_merge_existing_dest_succeeds_with_overwrite(store: Path) -> None:
    merge_profiles(store, "base", "override", "merged", "pass", "pass", "pass")
    merge_profiles(store, "base", "override", "merged", "pass", "pass", "pass", overwrite=True)
    text = load_profile(store, "merged", "pass")
    assert text  # just verify it loads
