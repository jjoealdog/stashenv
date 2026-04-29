import pytest
from pathlib import Path
from stashenv.group import (
    add_to_group,
    remove_from_group,
    list_groups,
    get_group_members,
    get_profile_groups,
    delete_group,
    GroupNotFoundError,
    ProfileNotInGroupError,
)


@pytest.fixture
def store_dir(tmp_path: Path) -> Path:
    return tmp_path


def test_list_groups_empty_when_no_file(store_dir):
    assert list_groups(store_dir) == []


def test_add_to_group_creates_groups_file(store_dir):
    add_to_group(store_dir, "prod", "production")
    assert (store_dir / ".groups.json").exists()


def test_add_to_group_stores_profile(store_dir):
    add_to_group(store_dir, "prod", "production")
    assert "production" in get_group_members(store_dir, "prod")


def test_add_multiple_profiles_to_same_group(store_dir):
    add_to_group(store_dir, "staging", "staging-us")
    add_to_group(store_dir, "staging", "staging-eu")
    members = get_group_members(store_dir, "staging")
    assert "staging-us" in members
    assert "staging-eu" in members


def test_add_duplicate_profile_is_idempotent(store_dir):
    add_to_group(store_dir, "prod", "production")
    add_to_group(store_dir, "prod", "production")
    assert get_group_members(store_dir, "prod").count("production") == 1


def test_list_groups_returns_all_groups(store_dir):
    add_to_group(store_dir, "prod", "p1")
    add_to_group(store_dir, "dev", "d1")
    assert sorted(list_groups(store_dir)) == ["dev", "prod"]


def test_get_group_members_raises_for_unknown_group(store_dir):
    with pytest.raises(GroupNotFoundError):
        get_group_members(store_dir, "nonexistent")


def test_remove_from_group_removes_profile(store_dir):
    add_to_group(store_dir, "prod", "production")
    remove_from_group(store_dir, "prod", "production")
    assert "prod" not in list_groups(store_dir)


def test_remove_from_group_missing_group_raises(store_dir):
    with pytest.raises(GroupNotFoundError):
        remove_from_group(store_dir, "ghost", "x")


def test_remove_from_group_missing_profile_raises(store_dir):
    add_to_group(store_dir, "prod", "production")
    with pytest.raises(ProfileNotInGroupError):
        remove_from_group(store_dir, "prod", "other")


def test_get_profile_groups_returns_groups(store_dir):
    add_to_group(store_dir, "prod", "shared")
    add_to_group(store_dir, "staging", "shared")
    groups = get_profile_groups(store_dir, "shared")
    assert "prod" in groups
    assert "staging" in groups


def test_get_profile_groups_empty_when_not_in_any(store_dir):
    assert get_profile_groups(store_dir, "loner") == []


def test_delete_group_removes_group(store_dir):
    add_to_group(store_dir, "temp", "p1")
    delete_group(store_dir, "temp")
    assert "temp" not in list_groups(store_dir)


def test_delete_group_missing_raises(store_dir):
    with pytest.raises(GroupNotFoundError):
        delete_group(store_dir, "missing")
