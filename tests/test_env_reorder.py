"""Tests for stashenv.env_reorder."""

import pytest
from pathlib import Path

from stashenv.env_reorder import reorder_env_text, reorder_profile, ReorderResult
from stashenv.store import save_profile, load_profile


ENV_TEXT = """ALPHA=1
BETA=2
GAMMA=3
"""


# ---------------------------------------------------------------------------
# reorder_env_text unit tests
# ---------------------------------------------------------------------------

def test_reorder_places_keys_in_given_order():
    result = reorder_env_text(ENV_TEXT, ["GAMMA", "ALPHA", "BETA"])
    lines = [l for l in result.splitlines() if "=" in l]
    assert [l.split("=")[0] for l in lines] == ["GAMMA", "ALPHA", "BETA"]


def test_reorder_partial_order_appends_rest():
    result = reorder_env_text(ENV_TEXT, ["GAMMA"])
    lines = [l for l in result.splitlines() if "=" in l]
    keys = [l.split("=")[0] for l in lines]
    assert keys[0] == "GAMMA"
    assert set(keys) == {"ALPHA", "BETA", "GAMMA"}


def test_reorder_drop_unspecified_when_flag_false():
    result = reorder_env_text(ENV_TEXT, ["GAMMA"], keep_unspecified=False)
    lines = [l for l in result.splitlines() if "=" in l]
    assert [l.split("=")[0] for l in lines] == ["GAMMA"]


def test_reorder_preserves_values():
    result = reorder_env_text(ENV_TEXT, ["BETA", "ALPHA", "GAMMA"])
    assert "ALPHA=1" in result
    assert "BETA=2" in result
    assert "GAMMA=3" in result


def test_reorder_comment_travels_with_key():
    text = "# comment for B\nBETA=2\nALPHA=1\n"
    result = reorder_env_text(text, ["ALPHA", "BETA"])
    idx_alpha = result.index("ALPHA")
    idx_comment = result.index("# comment for B")
    idx_beta = result.index("BETA")
    assert idx_alpha < idx_comment < idx_beta


def test_reorder_unknown_keys_in_order_ignored():
    result = reorder_env_text(ENV_TEXT, ["DELTA", "ALPHA"])
    lines = [l for l in result.splitlines() if "=" in l]
    keys = [l.split("=")[0] for l in lines]
    assert "DELTA" not in keys
    assert "ALPHA" in keys


def test_reorder_already_ordered_unchanged():
    result = reorder_env_text(ENV_TEXT, ["ALPHA", "BETA", "GAMMA"])
    assert result == ENV_TEXT


# ---------------------------------------------------------------------------
# reorder_profile integration tests
# ---------------------------------------------------------------------------

@pytest.fixture()
def store(tmp_path):
    save_profile(tmp_path, "dev", "secret", ENV_TEXT)
    return tmp_path


def test_reorder_profile_returns_result(store):
    r = reorder_profile(store, "dev", "secret", ["GAMMA", "BETA", "ALPHA"])
    assert isinstance(r, ReorderResult)
    assert r.profile == "dev"


def test_reorder_profile_changed_flag_true_when_order_differs(store):
    r = reorder_profile(store, "dev", "secret", ["GAMMA", "BETA", "ALPHA"])
    assert r.changed is True


def test_reorder_profile_changed_flag_false_when_same_order(store):
    r = reorder_profile(store, "dev", "secret", ["ALPHA", "BETA", "GAMMA"])
    assert r.changed is False


def test_reorder_profile_persists_new_order(store):
    reorder_profile(store, "dev", "secret", ["GAMMA", "ALPHA", "BETA"])
    text = load_profile(store, "dev", "secret")
    lines = [l for l in text.splitlines() if "=" in l]
    keys = [l.split("=")[0] for l in lines]
    assert keys == ["GAMMA", "ALPHA", "BETA"]


def test_reorder_profile_original_order_recorded(store):
    r = reorder_profile(store, "dev", "secret", ["GAMMA", "BETA", "ALPHA"])
    assert r.original_order == ["ALPHA", "BETA", "GAMMA"]
