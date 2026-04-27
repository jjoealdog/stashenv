"""Tests for stashenv/tags.py"""

import pytest
from pathlib import Path

from stashenv.tags import (
    add_tag,
    remove_tag,
    get_tags,
    profiles_by_tag,
    delete_profile_tags,
)


@pytest.fixture
def store_dir(tmp_path):
    return tmp_path


def test_get_tags_empty_when_no_tags_file(store_dir):
    assert get_tags("dev", store_dir=store_dir) == []


def test_add_tag_creates_tags_file(store_dir):
    add_tag("dev", "production", store_dir=store_dir)
    assert (store_dir / "tags.json").exists()


def test_add_tag_associates_tag_with_profile(store_dir):
    add_tag("dev", "staging", store_dir=store_dir)
    assert "staging" in get_tags("dev", store_dir=store_dir)


def test_add_multiple_tags(store_dir):
    add_tag("dev", "staging", store_dir=store_dir)
    add_tag("dev", "backend", store_dir=store_dir)
    tags = get_tags("dev", store_dir=store_dir)
    assert "staging" in tags
    assert "backend" in tags


def test_add_duplicate_tag_is_idempotent(store_dir):
    add_tag("dev", "staging", store_dir=store_dir)
    add_tag("dev", "staging", store_dir=store_dir)
    assert get_tags("dev", store_dir=store_dir).count("staging") == 1


def test_remove_tag(store_dir):
    add_tag("dev", "staging", store_dir=store_dir)
    remove_tag("dev", "staging", store_dir=store_dir)
    assert "staging" not in get_tags("dev", store_dir=store_dir)


def test_remove_missing_tag_does_not_raise(store_dir):
    remove_tag("dev", "nonexistent", store_dir=store_dir)


def test_profiles_by_tag_returns_matching_profiles(store_dir):
    add_tag("dev", "backend", store_dir=store_dir)
    add_tag("prod", "backend", store_dir=store_dir)
    add_tag("staging", "frontend", store_dir=store_dir)
    result = profiles_by_tag("backend", store_dir=store_dir)
    assert "dev" in result
    assert "prod" in result
    assert "staging" not in result


def test_profiles_by_tag_empty_when_no_match(store_dir):
    assert profiles_by_tag("nope", store_dir=store_dir) == []


def test_delete_profile_tags_removes_entry(store_dir):
    add_tag("dev", "staging", store_dir=store_dir)
    delete_profile_tags("dev", store_dir=store_dir)
    assert get_tags("dev", store_dir=store_dir) == []


def test_delete_profile_tags_does_not_affect_others(store_dir):
    add_tag("dev", "staging", store_dir=store_dir)
    add_tag("prod", "live", store_dir=store_dir)
    delete_profile_tags("dev", store_dir=store_dir)
    assert "live" in get_tags("prod", store_dir=store_dir)
