"""Tests for stashenv.rotate."""

import pytest
from pathlib import Path
from stashenv.store import save_profile, load_profile
from stashenv.rotate import (
    rotate_profile,
    rotate_all_profiles,
    ProfileNotFoundError,
    RotationError,
)


@pytest.fixture
def store(tmp_path: Path) -> Path:
    return tmp_path / "store"


def test_rotate_profile_allows_load_with_new_password(store: Path) -> None:
    save_profile("dev", b"KEY=value", "oldpass", store)
    rotate_profile("dev", "oldpass", "newpass", store)
    data = load_profile("dev", "newpass", store)
    assert data == b"KEY=value"


def test_rotate_profile_old_password_no_longer_works(store: Path) -> None:
    save_profile("dev", b"KEY=value", "oldpass", store)
    rotate_profile("dev", "oldpass", "newpass", store)
    with pytest.raises(Exception):
        load_profile("dev", "oldpass", store)


def test_rotate_profile_missing_raises(store: Path) -> None:
    with pytest.raises(ProfileNotFoundError):
        rotate_profile("ghost", "a", "b", store)


def test_rotate_profile_wrong_old_password_raises(store: Path) -> None:
    save_profile("dev", b"KEY=value", "correct", store)
    with pytest.raises(RotationError):
        rotate_profile("dev", "wrong", "newpass", store)


def test_rotate_all_profiles_returns_succeeded_list(store: Path) -> None:
    save_profile("dev", b"A=1", "pass", store)
    save_profile("prod", b"B=2", "pass", store)
    succeeded, failed = rotate_all_profiles("pass", "newpass", store)
    assert set(succeeded) == {"dev", "prod"}
    assert failed == []


def test_rotate_all_profiles_partial_failure(store: Path) -> None:
    save_profile("dev", b"A=1", "pass", store)
    save_profile("prod", b"B=2", "different", store)
    succeeded, failed = rotate_all_profiles("pass", "newpass", store)
    assert "dev" in succeeded
    assert "prod" in failed


def test_rotate_all_profiles_empty_store(store: Path) -> None:
    succeeded, failed = rotate_all_profiles("pass", "newpass", store)
    assert succeeded == []
    assert failed == []
