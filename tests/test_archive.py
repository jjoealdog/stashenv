"""Tests for stashenv.archive."""

import pytest
from pathlib import Path

from stashenv.store import save_profile, load_profile, list_profiles
from stashenv.archive import (
    archive_profiles,
    restore_profiles,
    ArchiveError,
    ProfileNotFoundError,
)


@pytest.fixture
def store(tmp_path):
    d = tmp_path / "store"
    d.mkdir()
    save_profile(d, "dev", b"KEY=dev_value\nDEBUG=true", "pw1")
    save_profile(d, "prod", b"KEY=prod_value\nDEBUG=false", "pw2")
    save_profile(d, "staging", b"KEY=staging_value", "pw3")
    return d


def test_archive_creates_file(store, tmp_path):
    out = tmp_path / "backup.tar.gz"
    archive_profiles(store, out)
    assert out.exists()


def test_archive_returns_profile_names(store, tmp_path):
    out = tmp_path / "backup.tar.gz"
    names = archive_profiles(store, out)
    assert set(names) == {"dev", "prod", "staging"}


def test_archive_subset_of_profiles(store, tmp_path):
    out = tmp_path / "partial.tar.gz"
    names = archive_profiles(store, out, profiles=["dev", "prod"])
    assert set(names) == {"dev", "prod"}


def test_archive_missing_profile_raises(store, tmp_path):
    out = tmp_path / "bad.tar.gz"
    with pytest.raises(ProfileNotFoundError):
        archive_profiles(store, out, profiles=["nonexistent"])


def test_restore_recreates_profiles(store, tmp_path):
    out = tmp_path / "backup.tar.gz"
    archive_profiles(store, out)

    new_store = tmp_path / "restored"
    new_store.mkdir()
    restored = restore_profiles(new_store, out)

    assert set(restored) == {"dev", "prod", "staging"}
    assert set(list_profiles(new_store)) == {"dev", "prod", "staging"}


def test_restore_profiles_are_loadable(store, tmp_path):
    out = tmp_path / "backup.tar.gz"
    archive_profiles(store, out)

    new_store = tmp_path / "restored"
    new_store.mkdir()
    restore_profiles(new_store, out)

    data = load_profile(new_store, "dev", "pw1")
    assert b"KEY=dev_value" in data


def test_restore_raises_on_existing_profile_without_overwrite(store, tmp_path):
    out = tmp_path / "backup.tar.gz"
    archive_profiles(store, out)
    with pytest.raises(ArchiveError, match="already exists"):
        restore_profiles(store, out, overwrite=False)


def test_restore_overwrite_replaces_profile(store, tmp_path):
    out = tmp_path / "backup.tar.gz"
    archive_profiles(store, out, profiles=["dev"])
    # overwrite the existing dev profile
    save_profile(store, "dev", b"KEY=changed", "newpw")
    restore_profiles(store, out, overwrite=True)
    data = load_profile(store, "dev", "pw1")
    assert b"KEY=dev_value" in data


def test_restore_missing_archive_raises(tmp_path):
    store = tmp_path / "store"
    store.mkdir()
    with pytest.raises(ArchiveError, match="not found"):
        restore_profiles(store, tmp_path / "ghost.tar.gz")
