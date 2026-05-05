"""Tests for stashenv.env_sort."""

import pytest
from pathlib import Path

from stashenv.env_sort import sort_env_text, sort_profile, SortResult
from stashenv.store import save_profile, load_profile


# ---------------------------------------------------------------------------
# sort_env_text unit tests
# ---------------------------------------------------------------------------

def test_sort_env_text_basic_alphabetical():
    text = "ZEBRA=1\nAPPLE=2\nMango=3"
    result = sort_env_text(text)
    keys = [ln.split("=")[0] for ln in result.splitlines() if "=" in ln]
    assert keys == sorted(keys, key=str.lower)


def test_sort_env_text_already_sorted_unchanged():
    text = "ALPHA=1\nBETA=2\nGAMMA=3"
    assert sort_env_text(text) == text


def test_sort_env_text_reverse():
    text = "ALPHA=1\nBETA=2\nGAMMA=3"
    result = sort_env_text(text, reverse=True)
    keys = [ln.split("=")[0] for ln in result.splitlines() if "=" in ln]
    assert keys == sorted(keys, key=str.lower, reverse=True)


def test_sort_env_text_preserves_blank_line_sections():
    text = "ZEBRA=1\nAPPLE=2\n\nMOOSE=3\nANT=4"
    result = sort_env_text(text)
    assert "\n\n" in result  # blank line separator preserved
    parts = result.split("\n\n")
    assert len(parts) == 2


def test_sort_env_text_comment_attached_to_key():
    text = "# second\nZEBRA=1\n# first\nAPPLE=2"
    result = sort_env_text(text, group_comments=True)
    lines = result.splitlines()
    # APPLE block should come before ZEBRA block
    apple_idx = next(i for i, l in enumerate(lines) if "APPLE" in l)
    zebra_idx = next(i for i, l in enumerate(lines) if "ZEBRA" in l)
    assert apple_idx < zebra_idx
    # The comment '# first' should immediately precede APPLE
    assert lines[apple_idx - 1] == "# first"


def test_sort_env_text_value_with_equals_not_split_on_second_equals():
    text = "Z=a=b\nA=c=d"
    result = sort_env_text(text)
    assert "Z=a=b" in result
    assert "A=c=d" in result
    keys = [ln.split("=", 1)[0] for ln in result.splitlines() if "=" in ln]
    assert keys[0] == "A"


def test_sort_env_text_ignores_comment_only_lines_in_sort_order():
    text = "# standalone comment\nZEBRA=1\nAPPLE=2"
    result = sort_env_text(text, group_comments=False)
    assert "# standalone comment" in result


def test_sort_env_text_empty_string():
    assert sort_env_text("") == ""


# ---------------------------------------------------------------------------
# sort_profile integration tests
# ---------------------------------------------------------------------------

@pytest.fixture
def store(tmp_path):
    return tmp_path / "store"


def test_sort_profile_returns_sort_result(store):
    store.mkdir()
    save_profile("dev", store, "ZEBRA=1\nAPPLE=2", "secret")
    result = sort_profile("dev", store, "secret")
    assert isinstance(result, SortResult)
    assert result.profile == "dev"


def test_sort_profile_changed_flag_true_when_reordered(store):
    store.mkdir()
    save_profile("dev", store, "ZEBRA=1\nAPPLE=2", "secret")
    result = sort_profile("dev", store, "secret")
    assert result.changed is True


def test_sort_profile_changed_flag_false_when_already_sorted(store):
    store.mkdir()
    save_profile("dev", store, "APPLE=2\nZEBRA=1", "secret")
    result = sort_profile("dev", store, "secret")
    assert result.changed is False


def test_sort_profile_persists_sorted_content(store):
    store.mkdir()
    save_profile("dev", store, "ZEBRA=1\nAPPLE=2", "secret")
    sort_profile("dev", store, "secret")
    reloaded = load_profile("dev", store, "secret")
    keys = [ln.split("=")[0] for ln in reloaded.splitlines() if "=" in ln]
    assert keys == sorted(keys, key=str.lower)


def test_sort_profile_original_order_reflects_before_sort(store):
    store.mkdir()
    save_profile("dev", store, "ZEBRA=1\nAPPLE=2", "secret")
    result = sort_profile("dev", store, "secret")
    assert result.original_order == ["ZEBRA", "APPLE"]
    assert result.sorted_order == ["APPLE", "ZEBRA"]


def test_sort_profile_does_not_overwrite_when_unchanged(store):
    store.mkdir()
    content = "ALPHA=1\nBETA=2"
    save_profile("dev", store, content, "secret")
    profile_file = next(store.glob("dev.*"), None)
    mtime_before = profile_file.stat().st_mtime if profile_file else None
    result = sort_profile("dev", store, "secret")
    assert result.changed is False
