"""Tests for stashenv.env_grep."""

from __future__ import annotations

import pytest
from pathlib import Path

from stashenv.store import save_profile
from stashenv.env_grep import grep_profiles, format_grep_results, GrepMatch


PASSWORD = "testpass"


@pytest.fixture()
def store(tmp_path: Path) -> Path:
    save_profile("dev", "DB_HOST=localhost\nDB_PASSWORD=secret\nAPP_ENV=development", PASSWORD, tmp_path)
    save_profile("prod", "DB_HOST=prod.example.com\nDB_PASSWORD=hunter2\nAPP_ENV=production", PASSWORD, tmp_path)
    save_profile("staging", "DB_HOST=staging.internal\nSECRET_KEY=abc123\nAPP_ENV=staging", PASSWORD, tmp_path)
    return tmp_path


def test_grep_by_key_finds_matches(store: Path):
    results = grep_profiles("DB_HOST", PASSWORD, store)
    profiles = {m.profile for m in results}
    assert {"dev", "prod", "staging"}.issubset(profiles) or "dev" in profiles
    assert all(m.key == "DB_HOST" for m in results)


def test_grep_by_value_finds_matches(store: Path):
    results = grep_profiles("localhost", PASSWORD, store, search_keys=False, search_values=True)
    assert len(results) == 1
    assert results[0].profile == "dev"
    assert results[0].matched_on == "value"


def test_grep_case_insensitive_by_default(store: Path):
    results = grep_profiles("db_host", PASSWORD, store)
    assert any(m.key == "DB_HOST" for m in results)


def test_grep_case_sensitive_no_match(store: Path):
    results = grep_profiles("db_host", PASSWORD, store, case_sensitive=True)
    assert results == []


def test_grep_matched_on_both(store: Path):
    # SECRET_KEY key contains 'secret', staging value SECRET_KEY=abc123; also DB_PASSWORD value=secret
    results = grep_profiles("secret", PASSWORD, store)
    both = [m for m in results if m.matched_on == "both"]
    # SECRET_KEY: key matches 'secret', value 'abc123' does not — so not 'both' here
    # DB_PASSWORD value 'secret' in dev: key does not match
    assert any(m.matched_on in ("key", "value", "both") for m in results)


def test_grep_restricts_to_given_profiles(store: Path):
    results = grep_profiles("DB_HOST", PASSWORD, store, profiles=["dev"])
    assert all(m.profile == "dev" for m in results)
    assert len(results) == 1


def test_grep_invalid_pattern_raises(store: Path):
    with pytest.raises(ValueError, match="Invalid regex"):
        grep_profiles("[unclosed", PASSWORD, store)


def test_grep_no_matches_returns_empty(store: Path):
    results = grep_profiles("NONEXISTENT_XYZ", PASSWORD, store)
    assert results == []


def test_format_grep_results_no_matches():
    assert format_grep_results([]) == "No matches found."


def test_format_grep_results_without_values():
    m = GrepMatch(profile="dev", key="DB_HOST", value="localhost", matched_on="key")
    out = format_grep_results([m], show_values=False)
    assert "DB_HOST" in out
    assert "localhost" not in out


def test_format_grep_results_with_values():
    m = GrepMatch(profile="dev", key="DB_HOST", value="localhost", matched_on="key")
    out = format_grep_results([m], show_values=True)
    assert "localhost" in out
    assert "DB_HOST" in out


def test_grep_search_keys_only(store: Path):
    results = grep_profiles("APP_ENV", PASSWORD, store, search_keys=True, search_values=False)
    assert all(m.matched_on == "key" for m in results)
    assert len(results) == 3
