"""Tests for stashenv.prune."""

from __future__ import annotations

import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from stashenv.store import save_profile, list_profiles
from stashenv.expire import set_expiry
from stashenv.prune import prune_expired, prune_older_than


PASSWORD = "hunter2"
ENV_TEXT = b"KEY=value\nFOO=bar\n"


@pytest.fixture()
def store(tmp_path):
    return tmp_path / "store"


def _save(store_dir, name):
    save_profile(store_dir, name, ENV_TEXT, PASSWORD)


# ---------------------------------------------------------------------------
# prune_expired
# ---------------------------------------------------------------------------

def test_prune_expired_removes_expired_profiles(store):
    _save(store, "old")
    past = datetime.now(tz=timezone.utc) - timedelta(days=1)
    set_expiry(store, "old", past)
    result = prune_expired(store_dir=store)
    assert "old" in result.pruned
    assert "old" not in list_profiles(store)


def test_prune_expired_keeps_future_profiles(store):
    _save(store, "fresh")
    future = datetime.now(tz=timezone.utc) + timedelta(days=30)
    set_expiry(store, "fresh", future)
    result = prune_expired(store_dir=store)
    assert "fresh" not in result.pruned
    assert "fresh" in list_profiles(store)


def test_prune_expired_skips_profiles_without_expiry(store):
    _save(store, "noexpiry")
    result = prune_expired(store_dir=store)
    assert "noexpiry" in result.skipped
    assert "noexpiry" in list_profiles(store)


def test_prune_expired_returns_correct_counts(store):
    _save(store, "a")
    _save(store, "b")
    past = datetime.now(tz=timezone.utc) - timedelta(seconds=1)
    set_expiry(store, "a", past)
    result = prune_expired(store_dir=store)
    assert result.total == 1
    assert len(result.skipped) == 1


# ---------------------------------------------------------------------------
# prune_older_than
# ---------------------------------------------------------------------------

def test_prune_older_than_removes_old_files(store, tmp_path):
    _save(store, "ancient")
    from stashenv.store import _profile_path
    p = _profile_path(store, "ancient")
    # backdate mtime by 10 days
    old_ts = time.time() - 10 * 86400
    import os
    os.utime(p, (old_ts, old_ts))
    result = prune_older_than(days=5, store_dir=store)
    assert "ancient" in result.pruned
    assert "ancient" not in list_profiles(store)


def test_prune_older_than_keeps_recent_files(store):
    _save(store, "recent")
    result = prune_older_than(days=30, store_dir=store)
    assert "recent" not in result.pruned
    assert "recent" in list_profiles(store)


def test_prune_older_than_empty_store_returns_empty(store):
    result = prune_older_than(days=1, store_dir=store)
    assert result.pruned == []
    assert result.skipped == []
