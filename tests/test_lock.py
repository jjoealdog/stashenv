import pytest
from pathlib import Path
from stashenv.lock import (
    lock_profile,
    unlock_profile,
    is_locked,
    list_locked,
    ProfileLockedError,
)


@pytest.fixture
def store_dir(tmp_path):
    return tmp_path


def test_is_locked_false_when_no_locks_file(store_dir):
    assert is_locked(store_dir, "prod") is False


def test_lock_profile_creates_locks_file(store_dir):
    lock_profile(store_dir, "prod")
    assert (store_dir / ".locks.json").exists()


def test_lock_profile_marks_profile_locked(store_dir):
    lock_profile(store_dir, "prod")
    assert is_locked(store_dir, "prod") is True


def test_unlock_profile_removes_lock(store_dir):
    lock_profile(store_dir, "prod")
    unlock_profile(store_dir, "prod")
    assert is_locked(store_dir, "prod") is False


def test_unlock_nonexistent_profile_does_not_raise(store_dir):
    unlock_profile(store_dir, "ghost")  # should not raise


def test_list_locked_empty_when_no_locks(store_dir):
    assert list_locked(store_dir) == []


def test_list_locked_returns_all_locked_profiles(store_dir):
    lock_profile(store_dir, "prod")
    lock_profile(store_dir, "staging")
    assert list_locked(store_dir) == ["prod", "staging"]


def test_list_locked_excludes_unlocked_profiles(store_dir):
    lock_profile(store_dir, "prod")
    lock_profile(store_dir, "staging")
    unlock_profile(store_dir, "staging")
    assert list_locked(store_dir) == ["prod"]


def test_lock_multiple_profiles_independently(store_dir):
    lock_profile(store_dir, "prod")
    assert is_locked(store_dir, "dev") is False
    assert is_locked(store_dir, "prod") is True
