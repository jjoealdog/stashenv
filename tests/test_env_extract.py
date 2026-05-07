"""Tests for stashenv.env_extract."""

import pytest

from stashenv.env_extract import (
    ExtractResult,
    NoKeysMatchedError,
    ProfileNotFoundError,
    extract_profile,
)
from stashenv.store import load_profile, save_profile


PASSWORD = "hunter2"

ENV_TEXT = """DB_HOST=localhost
DB_PORT=5432
API_KEY=secret
DEBUG=true
"""


@pytest.fixture()
def store(tmp_path):
    save_profile("base", ENV_TEXT, PASSWORD, store_dir=tmp_path)
    return tmp_path


def test_extract_creates_destination_profile(store):
    extract_profile("base", "db_only", ["DB_HOST", "DB_PORT"], PASSWORD, store_dir=store)
    profiles = [p.stem for p in store.iterdir() if p.suffix == ".enc"]
    assert "db_only" in profiles


def test_extract_destination_contains_only_requested_keys(store):
    extract_profile("base", "db_only", ["DB_HOST", "DB_PORT"], PASSWORD, store_dir=store)
    text = load_profile("db_only", PASSWORD, store_dir=store)
    assert "DB_HOST" in text
    assert "DB_PORT" in text
    assert "API_KEY" not in text
    assert "DEBUG" not in text


def test_extract_result_tracks_extracted_keys(store):
    result = extract_profile("base", "api", ["API_KEY"], PASSWORD, store_dir=store)
    assert result.extracted_keys == ["API_KEY"]
    assert result.total_extracted == 1


def test_extract_result_tracks_skipped_keys(store):
    result = extract_profile(
        "base", "partial", ["API_KEY", "NONEXISTENT"], PASSWORD, store_dir=store
    )
    assert "NONEXISTENT" in result.skipped_keys
    assert "API_KEY" in result.extracted_keys


def test_extract_missing_source_raises(store):
    with pytest.raises(ProfileNotFoundError):
        extract_profile("ghost", "dest", ["DB_HOST"], PASSWORD, store_dir=store)


def test_extract_strict_raises_when_no_keys_match(store):
    with pytest.raises(NoKeysMatchedError):
        extract_profile(
            "base", "empty", ["DOES_NOT_EXIST"], PASSWORD, store_dir=store, strict=True
        )


def test_extract_non_strict_creates_empty_profile_when_no_keys_match(store):
    result = extract_profile(
        "base", "empty", ["DOES_NOT_EXIST"], PASSWORD, store_dir=store, strict=False
    )
    assert result.total_extracted == 0
    text = load_profile("empty", PASSWORD, store_dir=store)
    assert text.strip() == ""


def test_extract_result_source_and_destination_set(store):
    result = extract_profile("base", "out", ["DEBUG"], PASSWORD, store_dir=store)
    assert result.source == "base"
    assert result.destination == "out"


def test_extract_preserves_values(store):
    extract_profile("base", "val_check", ["DB_HOST"], PASSWORD, store_dir=store)
    text = load_profile("val_check", PASSWORD, store_dir=store)
    assert "DB_HOST=localhost" in text
