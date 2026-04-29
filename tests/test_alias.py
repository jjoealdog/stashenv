"""Tests for stashenv.alias."""

import pytest
from pathlib import Path

from stashenv.alias import (
    set_alias,
    remove_alias,
    resolve_alias,
    list_aliases,
    AliasNotFoundError,
    AliasAlreadyExistsError,
)


@pytest.fixture
def store_dir(tmp_path: Path) -> Path:
    store = tmp_path / ".stashenv"
    store.mkdir()
    return store


def test_list_aliases_empty_when_no_file(store_dir):
    assert list_aliases(store_dir) == {}


def test_set_alias_creates_file(store_dir):
    set_alias(store_dir, "prod", "production")
    assert (store_dir / ".aliases.json").exists()


def test_set_alias_stores_mapping(store_dir):
    set_alias(store_dir, "prod", "production")
    assert list_aliases(store_dir) == {"prod": "production"}


def test_set_multiple_aliases(store_dir):
    set_alias(store_dir, "prod", "production")
    set_alias(store_dir, "dev", "development")
    aliases = list_aliases(store_dir)
    assert aliases["prod"] == "production"
    assert aliases["dev"] == "development"


def test_set_alias_raises_if_already_exists(store_dir):
    set_alias(store_dir, "prod", "production")
    with pytest.raises(AliasAlreadyExistsError):
        set_alias(store_dir, "prod", "other_profile")


def test_set_alias_overwrite_allowed(store_dir):
    set_alias(store_dir, "prod", "production")
    set_alias(store_dir, "prod", "production-v2", overwrite=True)
    assert resolve_alias(store_dir, "prod") == "production-v2"


def test_resolve_alias_returns_profile(store_dir):
    set_alias(store_dir, "s", "staging")
    assert resolve_alias(store_dir, "s") == "staging"


def test_resolve_alias_raises_if_missing(store_dir):
    with pytest.raises(AliasNotFoundError):
        resolve_alias(store_dir, "nonexistent")


def test_remove_alias_deletes_mapping(store_dir):
    set_alias(store_dir, "prod", "production")
    remove_alias(store_dir, "prod")
    assert "prod" not in list_aliases(store_dir)


def test_remove_alias_raises_if_missing(store_dir):
    with pytest.raises(AliasNotFoundError):
        remove_alias(store_dir, "ghost")


def test_set_alias_empty_name_raises(store_dir):
    with pytest.raises(ValueError):
        set_alias(store_dir, "", "production")


def test_set_alias_whitespace_name_raises(store_dir):
    with pytest.raises(ValueError):
        set_alias(store_dir, "   ", "production")
