"""Tests for stashenv.store — profile persistence layer."""

import pytest
from pathlib import Path

from stashenv.store import save_profile, load_profile, list_profiles, delete_profile

PROJECT = "my-project"
PASSWORD = "hunter2"
ENV_CONTENT = "DATABASE_URL=postgres://localhost/dev\nSECRET_KEY=abc123\n"


@pytest.fixture
def store(tmp_path):
    """Provide a temporary store base directory."""
    return tmp_path


def test_save_profile_creates_file(store):
    path = save_profile(PROJECT, "dev", ENV_CONTENT, PASSWORD, base=store)
    assert path.exists()
    assert path.suffix == ".enc"


def test_load_profile_roundtrip(store):
    save_profile(PROJECT, "dev", ENV_CONTENT, PASSWORD, base=store)
    result = load_profile(PROJECT, "dev", PASSWORD, base=store)
    assert result == ENV_CONTENT


def test_load_profile_wrong_password_raises(store):
    save_profile(PROJECT, "dev", ENV_CONTENT, PASSWORD, base=store)
    with pytest.raises(Exception):
        load_profile(PROJECT, "dev", "wrongpassword", base=store)


def test_load_missing_profile_raises(store):
    with pytest.raises(FileNotFoundError, match="Profile 'ghost' not found"):
        load_profile(PROJECT, "ghost", PASSWORD, base=store)


def test_list_profiles_empty(store):
    assert list_profiles(PROJECT, base=store) == []


def test_list_profiles_returns_names(store):
    save_profile(PROJECT, "dev", ENV_CONTENT, PASSWORD, base=store)
    save_profile(PROJECT, "staging", ENV_CONTENT, PASSWORD, base=store)
    profiles = list_profiles(PROJECT, base=store)
    assert set(profiles) == {"dev", "staging"}


def test_delete_profile_removes_file(store):
    save_profile(PROJECT, "dev", ENV_CONTENT, PASSWORD, base=store)
    result = delete_profile(PROJECT, "dev", base=store)
    assert result is True
    assert list_profiles(PROJECT, base=store) == []


def test_delete_nonexistent_profile_returns_false(store):
    result = delete_profile(PROJECT, "nope", base=store)
    assert result is False


def test_multiple_projects_are_isolated(store):
    save_profile("project-a", "dev", "A=1\n", PASSWORD, base=store)
    save_profile("project-b", "dev", "B=2\n", PASSWORD, base=store)
    assert list_profiles("project-a", base=store) == ["dev"]
    assert list_profiles("project-b", base=store) == ["dev"]
    content_a = load_profile("project-a", "dev", PASSWORD, base=store)
    assert content_a == "A=1\n"
