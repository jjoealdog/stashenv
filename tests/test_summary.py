"""Tests for stashenv.summary."""

from __future__ import annotations

import pytest
from pathlib import Path

from stashenv.store import save_profile
from stashenv.tags import add_tag
from stashenv.notes import set_note
from stashenv.lock import lock_profile
from stashenv.favorite import add_favorite
from stashenv.alias import set_alias
from stashenv.summary import summarise_profile, format_summary


PASSWORD = "hunter2"
PROFILE = "staging"
ENV_TEXT = "DB_HOST=localhost\nDB_PORT=5432\n"


@pytest.fixture()
def store(tmp_path: Path) -> Path:
    save_profile(tmp_path, PROFILE, ENV_TEXT, PASSWORD)
    return tmp_path


def test_summarise_returns_correct_name(store: Path) -> None:
    s = summarise_profile(store, PROFILE)
    assert s.name == PROFILE


def test_summarise_size_is_positive(store: Path) -> None:
    s = summarise_profile(store, PROFILE)
    assert s.size_bytes > 0


def test_summarise_tags_empty_by_default(store: Path) -> None:
    s = summarise_profile(store, PROFILE)
    assert s.tags == []


def test_summarise_reflects_added_tag(store: Path) -> None:
    add_tag(store, PROFILE, "infra")
    s = summarise_profile(store, PROFILE)
    assert "infra" in s.tags


def test_summarise_note_none_by_default(store: Path) -> None:
    s = summarise_profile(store, PROFILE)
    assert s.note is None


def test_summarise_reflects_note(store: Path) -> None:
    set_note(store, PROFILE, "used for staging deployments")
    s = summarise_profile(store, PROFILE)
    assert s.note == "used for staging deployments"


def test_summarise_locked_false_by_default(store: Path) -> None:
    s = summarise_profile(store, PROFILE)
    assert s.locked is False


def test_summarise_reflects_lock(store: Path) -> None:
    lock_profile(store, PROFILE)
    s = summarise_profile(store, PROFILE)
    assert s.locked is True


def test_summarise_is_favorite_false_by_default(store: Path) -> None:
    s = summarise_profile(store, PROFILE)
    assert s.is_favorite is False


def test_summarise_reflects_favorite(store: Path) -> None:
    add_favorite(store, PROFILE)
    s = summarise_profile(store, PROFILE)
    assert s.is_favorite is True


def test_summarise_aliases_empty_by_default(store: Path) -> None:
    s = summarise_profile(store, PROFILE)
    assert s.aliases == []


def test_summarise_reflects_alias(store: Path) -> None:
    set_alias(store, "stg", PROFILE)
    s = summarise_profile(store, PROFILE)
    assert "stg" in s.aliases


def test_summarise_missing_profile_raises(store: Path) -> None:
    with pytest.raises(FileNotFoundError):
        summarise_profile(store, "nonexistent")


def test_format_summary_contains_name(store: Path) -> None:
    s = summarise_profile(store, PROFILE)
    text = format_summary(s)
    assert PROFILE in text


def test_format_summary_contains_size(store: Path) -> None:
    s = summarise_profile(store, PROFILE)
    text = format_summary(s)
    assert "bytes" in text


def test_format_summary_shows_none_for_empty_note(store: Path) -> None:
    s = summarise_profile(store, PROFILE)
    text = format_summary(s)
    assert "(none)" in text
