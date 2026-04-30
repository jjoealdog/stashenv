"""Tests for stashenv.inherit."""
from __future__ import annotations

import pytest
from pathlib import Path

from stashenv.store import save_profile, load_profile
from stashenv.inherit import (
    resolve_profile,
    inherit_into_new,
    CircularInheritanceError,
    ProfileNotFoundError,
)


@pytest.fixture()
def store(tmp_path: Path, monkeypatch):
    monkeypatch.setenv("STASHENV_DIR", str(tmp_path))
    save_profile("base", "DB_HOST=localhost\nDB_PORT=5432\nDEBUG=false\n", "pass", store_dir=tmp_path)
    save_profile("dev", "DEBUG=true\nAPI_KEY=dev-secret\n", "pass", store_dir=tmp_path)
    return tmp_path


def test_resolve_inherits_missing_keys(store):
    merged = resolve_profile("dev", "pass", "base", "pass", store_dir=store)
    assert "DB_HOST=localhost" in merged
    assert "DB_PORT=5432" in merged


def test_resolve_profile_keys_take_precedence(store):
    merged = resolve_profile("dev", "pass", "base", "pass", store_dir=store)
    assert "DEBUG=true" in merged
    assert "DEBUG=false" not in merged


def test_resolve_profile_own_keys_present(store):
    merged = resolve_profile("dev", "pass", "base", "pass", store_dir=store)
    assert "API_KEY=dev-secret" in merged


def test_resolve_circular_raises(store):
    with pytest.raises(CircularInheritanceError):
        resolve_profile("dev", "pass", "dev", "pass", store_dir=store)


def test_resolve_missing_profile_raises(store):
    with pytest.raises(ProfileNotFoundError):
        resolve_profile("ghost", "pass", "base", "pass", store_dir=store)


def test_resolve_missing_base_raises(store):
    with pytest.raises(ProfileNotFoundError):
        resolve_profile("dev", "pass", "ghost", "pass", store_dir=store)


def test_inherit_into_new_creates_profile(store):
    inherit_into_new("dev", "pass", "base", "pass", "staging", "pass", store_dir=store)
    text = load_profile("staging", "pass", store_dir=store)
    assert "DB_HOST=localhost" in text
    assert "DEBUG=true" in text


def test_inherit_into_new_uses_dest_password(store):
    inherit_into_new("dev", "pass", "base", "pass", "staging", "newpass", store_dir=store)
    text = load_profile("staging", "newpass", store_dir=store)
    assert "API_KEY=dev-secret" in text


def test_inherit_into_new_wrong_password_raises(store):
    inherit_into_new("dev", "pass", "base", "pass", "staging", "newpass", store_dir=store)
    from stashenv.crypto import DecryptionError
    with pytest.raises(Exception):
        load_profile("staging", "wrongpass", store_dir=store)
