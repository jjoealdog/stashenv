"""Tests for stashenv.search."""

import pytest

from stashenv.store import save_profile
from stashenv.search import search_profiles, format_search_results, SearchMatch


PASSWORD = "hunter2"


@pytest.fixture()
def store(tmp_path):
    store_dir = str(tmp_path / "store")
    save_profile(store_dir, "dev", "DB_HOST=localhost\nDB_PORT=5432\nSECRET_KEY=abc123", PASSWORD)
    save_profile(store_dir, "prod", "DB_HOST=db.prod.example.com\nDB_PORT=5432\nAPI_KEY=xyz789", PASSWORD)
    save_profile(store_dir, "staging", "DB_HOST=db.staging.internal\nFEATURE_FLAG=true", PASSWORD)
    return store_dir


def test_search_by_key_finds_matches(store):
    results = search_profiles(store, PASSWORD, "DB_HOST", search_keys=True)
    profiles = {m.profile for m in results}
    assert profiles == {"dev", "prod", "staging"}


def test_search_by_key_partial_match(store):
    results = search_profiles(store, PASSWORD, "DB_", search_keys=True)
    keys = {m.key for m in results}
    assert "DB_HOST" in keys
    assert "DB_PORT" in keys


def test_search_by_value_finds_matches(store):
    results = search_profiles(store, PASSWORD, "5432", search_keys=False, search_values=True)
    assert len(results) == 2
    for m in results:
        assert m.matched_on == "value"


def test_search_case_insensitive_by_default(store):
    results = search_profiles(store, PASSWORD, "db_host", search_keys=True)
    assert len(results) == 3


def test_search_case_sensitive_no_match(store):
    results = search_profiles(store, PASSWORD, "db_host", search_keys=True, case_sensitive=True)
    assert results == []


def test_search_case_sensitive_match(store):
    results = search_profiles(store, PASSWORD, "DB_HOST", search_keys=True, case_sensitive=True)
    assert len(results) == 3


def test_search_wrong_password_skips_profile(store):
    # Should not raise; profiles that fail decryption are silently skipped.
    results = search_profiles(store, "wrongpassword", "DB_HOST", search_keys=True)
    assert results == []


def test_search_no_criteria_raises(store):
    with pytest.raises(ValueError, match="At least one"):
        search_profiles(store, PASSWORD, "DB", search_keys=False, search_values=False)


def test_format_search_results_no_matches():
    assert format_search_results([]) == "No matches found."


def test_format_search_results_groups_by_profile(store):
    results = search_profiles(store, PASSWORD, "DB_PORT", search_keys=True)
    output = format_search_results(results)
    assert "[dev]" in output
    assert "[prod]" in output
    assert "DB_PORT" in output


def test_format_search_results_show_values(store):
    results = search_profiles(store, PASSWORD, "SECRET_KEY", search_keys=True)
    output = format_search_results(results, show_values=True)
    assert "abc123" in output
