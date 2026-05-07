import pytest
from pathlib import Path

from stashenv.store import save_profile
from stashenv.env_flatten import flatten_profiles, FlattenResult, ProfileNotFoundError

PASSWORD = "testpass"


@pytest.fixture()
def store(tmp_path: Path) -> str:
    d = str(tmp_path)
    save_profile(d, "base", "KEY_A=alpha\nKEY_B=beta\nSHARED=from_base\n", PASSWORD)
    save_profile(d, "override", "SHARED=from_override\nKEY_C=gamma\n", PASSWORD)
    save_profile(d, "empty", "", PASSWORD)
    return d


def test_flatten_returns_flatten_result(store):
    result = flatten_profiles(store, ["base"], PASSWORD)
    assert isinstance(result, FlattenResult)


def test_flatten_single_profile_contains_all_keys(store):
    result = flatten_profiles(store, ["base"], PASSWORD)
    assert "KEY_A=alpha" in result.text
    assert "KEY_B=beta" in result.text


def test_flatten_last_profile_wins_on_duplicate(store):
    result = flatten_profiles(store, ["base", "override"], PASSWORD)
    assert "SHARED=from_override" in result.text
    assert "SHARED=from_base" not in result.text


def test_flatten_all_keys_present_across_profiles(store):
    result = flatten_profiles(store, ["base", "override"], PASSWORD)
    for key in ("KEY_A", "KEY_B", "KEY_C", "SHARED"):
        assert key in result.text


def test_flatten_key_sources_tracks_winning_profile(store):
    result = flatten_profiles(store, ["base", "override"], PASSWORD)
    assert result.key_sources["SHARED"] == "override"
    assert result.key_sources["KEY_A"] == "base"
    assert result.key_sources["KEY_C"] == "override"


def test_flatten_profiles_used_preserves_order(store):
    result = flatten_profiles(store, ["base", "override"], PASSWORD)
    assert result.profiles_used == ["base", "override"]


def test_flatten_total_keys_counts_unique_keys(store):
    result = flatten_profiles(store, ["base", "override"], PASSWORD)
    # KEY_A, KEY_B, SHARED, KEY_C
    assert result.total_keys == 4


def test_flatten_empty_profile_contributes_no_keys(store):
    result = flatten_profiles(store, ["empty"], PASSWORD)
    assert result.total_keys == 0
    assert result.text == ""


def test_flatten_missing_profile_raises(store):
    with pytest.raises(ProfileNotFoundError):
        flatten_profiles(store, ["nonexistent"], PASSWORD)


def test_flatten_missing_profile_in_list_raises(store):
    with pytest.raises(ProfileNotFoundError):
        flatten_profiles(store, ["base", "ghost"], PASSWORD)


def test_flatten_output_is_valid_env_format(store):
    result = flatten_profiles(store, ["base", "override"], PASSWORD)
    for line in result.text.strip().splitlines():
        assert "=" in line, f"Line missing '=': {line!r}"


def test_flatten_empty_profiles_list_returns_empty(store):
    result = flatten_profiles(store, [], PASSWORD)
    assert result.text == ""
    assert result.total_keys == 0
    assert result.profiles_used == []
