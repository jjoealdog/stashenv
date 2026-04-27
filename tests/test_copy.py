"""Tests for stashenv.copy module."""

import pytest
from pathlib import Path
from stashenv.store import save_profile, load_profile, list_profiles
from stashenv.copy import copy_profile, ProfileNotFoundError, ProfileAlreadyExistsError


@pytest.fixture
def store(tmp_path):
    return tmp_path


def test_copy_profile_creates_new_file(store):
    save_profile(store, "prod", b"KEY=value", "secret")
    copy_profile(store, "prod", "prod-backup")
    assert "prod-backup" in list_profiles(store)


def test_copy_profile_original_still_exists(store):
    save_profile(store, "prod", b"KEY=value", "secret")
    copy_profile(store, "prod", "prod-backup")
    assert "prod" in list_profiles(store)


def test_copy_profile_copy_is_loadable_with_same_password(store):
    save_profile(store, "prod", b"KEY=value", "secret")
    copy_profile(store, "prod", "prod-backup")
    data = load_profile(store, "prod-backup", "secret")
    assert data == b"KEY=value"


def test_copy_profile_missing_source_raises(store):
    with pytest.raises(ProfileNotFoundError):
        copy_profile(store, "nonexistent", "dest")


def test_copy_profile_destination_exists_raises(store):
    save_profile(store, "prod", b"KEY=1", "secret")
    save_profile(store, "staging", b"KEY=2", "secret")
    with pytest.raises(ProfileAlreadyExistsError):
        copy_profile(store, "prod", "staging")


def test_copy_profile_empty_source_raises(store):
    with pytest.raises(ValueError):
        copy_profile(store, "", "dest")


def test_copy_profile_empty_destination_raises(store):
    save_profile(store, "prod", b"KEY=value", "secret")
    with pytest.raises(ValueError):
        copy_profile(store, "prod", "")


def test_copy_does_not_affect_other_profiles(store):
    save_profile(store, "prod", b"A=1", "secret")
    save_profile(store, "dev", b"A=2", "secret")
    copy_profile(store, "prod", "prod-copy")
    assert load_profile(store, "dev", "secret") == b"A=2"
