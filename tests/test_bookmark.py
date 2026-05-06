"""Tests for stashenv.bookmark."""

import pytest
from pathlib import Path

from stashenv.bookmark import (
    add_bookmark,
    remove_bookmark,
    resolve_bookmark,
    list_bookmarks,
    BookmarkNotFoundError,
    BookmarkAlreadyExistsError,
)


@pytest.fixture()
def store_dir(tmp_path: Path) -> Path:
    return tmp_path


def test_list_bookmarks_empty_when_no_file(store_dir):
    assert list_bookmarks(store_dir) == {}


def test_add_bookmark_creates_file(store_dir):
    add_bookmark(store_dir, "prod", "production")
    assert (store_dir / ".bookmarks.json").exists()


def test_add_bookmark_stores_mapping(store_dir):
    add_bookmark(store_dir, "prod", "production")
    assert list_bookmarks(store_dir)["prod"] == "production"


def test_add_multiple_bookmarks(store_dir):
    add_bookmark(store_dir, "prod", "production")
    add_bookmark(store_dir, "dev", "development")
    bm = list_bookmarks(store_dir)
    assert bm["prod"] == "production"
    assert bm["dev"] == "development"


def test_add_duplicate_raises(store_dir):
    add_bookmark(store_dir, "prod", "production")
    with pytest.raises(BookmarkAlreadyExistsError):
        add_bookmark(store_dir, "prod", "other")


def test_add_duplicate_with_overwrite_succeeds(store_dir):
    add_bookmark(store_dir, "prod", "production")
    add_bookmark(store_dir, "prod", "staging", overwrite=True)
    assert resolve_bookmark(store_dir, "prod") == "staging"


def test_resolve_bookmark_returns_profile(store_dir):
    add_bookmark(store_dir, "shortcut", "myprofile")
    assert resolve_bookmark(store_dir, "shortcut") == "myprofile"


def test_resolve_missing_bookmark_raises(store_dir):
    with pytest.raises(BookmarkNotFoundError):
        resolve_bookmark(store_dir, "nope")


def test_remove_bookmark_deletes_entry(store_dir):
    add_bookmark(store_dir, "prod", "production")
    remove_bookmark(store_dir, "prod")
    assert "prod" not in list_bookmarks(store_dir)


def test_remove_missing_bookmark_raises(store_dir):
    with pytest.raises(BookmarkNotFoundError):
        remove_bookmark(store_dir, "ghost")


def test_add_empty_name_raises(store_dir):
    with pytest.raises(ValueError):
        add_bookmark(store_dir, "", "production")
