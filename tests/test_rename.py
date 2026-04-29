"""Tests for stashenv.rename module."""

import pytest
from pathlib import Path
from stashenv.store import save_profile, list_profiles
from stashenv.rename import rename_profile, ProfileNotFoundError, ProfileAlreadyExistsError


@pytest.fixture
def store(tmp_path):
    return tmp_path


def test_rename_profile_renames_file(store):
    save_profile(store, "dev", b"KEY=1", "pass")
    rename_profile(store, "dev", "development")
    profiles = list_profiles(store)
    assert "development" in profiles
    assert "dev" not in profiles


def test_rename_profile_missing_source_raises(store):
    with pytest.raises(ProfileNotFoundError):
        rename_profile(store, "ghost", "newname")


def test_rename_profile_target_exists_raises(store):
    save_profile(store, "dev", b"KEY=1", "pass")
    save_profile(store, "staging", b"KEY=2", "pass")
    with pytest.raises(ProfileAlreadyExistsError):
        rename_profile(store, "dev", "staging")


def test_rename_profile_empty_name_raises(store):
    save_profile(store, "dev", b"KEY=1", "pass")
    with pytest.raises(ValueError):
        rename_profile(store, "dev", "")
    with pytest.raises(ValueError):
        rename_profile(store, "", "newname")


def test_rename_profile_path_separator_raises(store):
    save_profile(store, "dev", b"KEY=1", "pass")
    with pytest.raises(ValueError):
        rename_profile(store, "dev", "sub/name")


def test_rename_profile_preserves_content(store):
    save_profile(store, "dev", b"KEY=hello", "mypassword")
    rename_profile(store, "dev", "production")
    from stashenv.store import load_profile
    content = load_profile(store, "production", "mypassword")
    assert content == b"KEY=hello"


def test_rename_does_not_leave_old_file(store):
    save_profile(store, "alpha", b"X=1", "pass")
    rename_profile(store, "alpha", "beta")
    from stashenv.store import _profile_path
    assert not _profile_path(store, "alpha").exists()


def test_rename_profile_same_name_raises(store):
    """Renaming a profile to its own name should raise ProfileAlreadyExistsError."""
    save_profile(store, "dev", b"KEY=1", "pass")
    with pytest.raises(ProfileAlreadyExistsError):
        rename_profile(store, "dev", "dev")
