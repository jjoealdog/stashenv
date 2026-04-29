import pytest
from pathlib import Path
from stashenv.store import save_profile
from stashenv.compare import compare_profiles, format_compare, CompareRow


PASSWORD = "testpass"


@pytest.fixture
def store(tmp_path):
    save_profile(tmp_path, "left", "KEY_A=foo\nKEY_B=bar\nSHARED=same\n", PASSWORD)
    save_profile(tmp_path, "right", "KEY_B=different\nSHARED=same\nKEY_C=new\n", PASSWORD)
    return tmp_path


def test_compare_returns_all_keys(store):
    rows = compare_profiles(store, "left", "right", PASSWORD)
    keys = [r.key for r in rows]
    assert "KEY_A" in keys
    assert "KEY_B" in keys
    assert "KEY_C" in keys
    assert "SHARED" in keys


def test_compare_detects_added_key(store):
    rows = compare_profiles(store, "left", "right", PASSWORD)
    row = next(r for r in rows if r.key == "KEY_C")
    assert row.status == "added"
    assert row.left_value is None
    assert row.right_value == "new"


def test_compare_detects_removed_key(store):
    rows = compare_profiles(store, "left", "right", PASSWORD)
    row = next(r for r in rows if r.key == "KEY_A")
    assert row.status == "removed"
    assert row.left_value == "foo"
    assert row.right_value is None


def test_compare_detects_changed_key(store):
    rows = compare_profiles(store, "left", "right", PASSWORD)
    row = next(r for r in rows if r.key == "KEY_B")
    assert row.status == "changed"
    assert row.left_value == "bar"
    assert row.right_value == "different"


def test_compare_detects_same_key(store):
    rows = compare_profiles(store, "left", "right", PASSWORD)
    row = next(r for r in rows if r.key == "SHARED")
    assert row.status == "same"
    assert row.is_same is True


def test_compare_keys_are_sorted(store):
    rows = compare_profiles(store, "left", "right", PASSWORD)
    keys = [r.key for r in rows]
    assert keys == sorted(keys)


def test_format_compare_contains_key_names(store):
    rows = compare_profiles(store, "left", "right", PASSWORD)
    output = format_compare(rows, "left", "right")
    assert "KEY_A" in output
    assert "KEY_B" in output


def test_format_compare_only_differences_hides_same(store):
    rows = compare_profiles(store, "left", "right", PASSWORD)
    output = format_compare(rows, "left", "right", only_differences=True)
    assert "SHARED" not in output
    assert "KEY_B" in output


def test_format_compare_show_values_includes_value(store):
    rows = compare_profiles(store, "left", "right", PASSWORD)
    output = format_compare(rows, "left", "right", show_values=True)
    assert "foo" in output
    assert "bar" in output


def test_format_compare_identical_profiles(store):
    save_profile(store, "copy", "KEY_A=foo\nKEY_B=bar\nSHARED=same\n", PASSWORD)
    rows = compare_profiles(store, "left", "copy", PASSWORD)
    output = format_compare(rows, "left", "copy", only_differences=True)
    assert "No differences" in output
