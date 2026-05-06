"""Tests for stashenv.env_rename_key."""

import pytest

from stashenv.env_rename_key import (
    KeyAlreadyExistsError,
    KeyNotFoundError,
    ProfileNotFoundError,
    RenameKeyResult,
    rename_key,
)
from stashenv.store import load_profile, save_profile


PASSWORD = "hunter2"


@pytest.fixture()
def store(tmp_path):
    save_profile(tmp_path, "dev", PASSWORD, "FOO=bar\nBAZ=qux\nDUP=first\nDUP2=second\n")
    return tmp_path


def test_rename_key_changes_key_name(store):
    rename_key(store, "dev", PASSWORD, "FOO", "FOO_NEW")
    text = load_profile(store, "dev", PASSWORD)
    assert "FOO_NEW=bar" in text
    assert "FOO=" not in text


def test_rename_key_preserves_value(store):
    rename_key(store, "dev", PASSWORD, "BAZ", "BAZ_RENAMED")
    text = load_profile(store, "dev", PASSWORD)
    assert "BAZ_RENAMED=qux" in text


def test_rename_key_preserves_other_keys(store):
    rename_key(store, "dev", PASSWORD, "FOO", "FOO_NEW")
    text = load_profile(store, "dev", PASSWORD)
    assert "BAZ=qux" in text


def test_rename_key_returns_result_object(store):
    result = rename_key(store, "dev", PASSWORD, "FOO", "FOO_NEW")
    assert isinstance(result, RenameKeyResult)
    assert result.old_key == "FOO"
    assert result.new_key == "FOO_NEW"
    assert result.old_value == "bar"
    assert result.profile == "dev"


def test_rename_key_missing_profile_raises(store):
    with pytest.raises(ProfileNotFoundError):
        rename_key(store, "ghost", PASSWORD, "FOO", "FOO_NEW")


def test_rename_key_missing_old_key_raises(store):
    with pytest.raises(KeyNotFoundError):
        rename_key(store, "dev", PASSWORD, "NOPE", "NOPE_NEW")


def test_rename_key_target_exists_raises(store):
    with pytest.raises(KeyAlreadyExistsError):
        rename_key(store, "dev", PASSWORD, "FOO", "BAZ")


def test_rename_key_overwrite_flag_allows_existing_target(store):
    rename_key(store, "dev", PASSWORD, "FOO", "BAZ", overwrite=True)
    text = load_profile(store, "dev", PASSWORD)
    assert "BAZ=bar" in text


def test_rename_key_profile_is_still_loadable(store):
    rename_key(store, "dev", PASSWORD, "FOO", "X")
    text = load_profile(store, "dev", PASSWORD)
    assert "X=bar" in text
