"""Tests for stashenv.ttl."""

from __future__ import annotations

import time
from pathlib import Path

import pytest

from stashenv.ttl import (
    TTLExpiredError,
    check_ttl,
    clear_ttl,
    get_ttl,
    is_stale,
    list_ttl,
    set_ttl,
)


@pytest.fixture()
def store_dir(tmp_path: Path) -> Path:
    return tmp_path


def test_get_ttl_returns_none_when_no_file(store_dir):
    assert get_ttl(store_dir, "dev") is None


def test_set_ttl_creates_file(store_dir):
    set_ttl(store_dir, "dev", 3600)
    assert (store_dir / ".ttl.json").exists()


def test_set_ttl_stores_record(store_dir):
    set_ttl(store_dir, "dev", 3600)
    rec = get_ttl(store_dir, "dev")
    assert rec is not None
    assert rec["ttl"] == 3600
    assert "created_at" in rec


def test_is_stale_false_for_fresh_profile(store_dir):
    set_ttl(store_dir, "dev", 3600)
    assert is_stale(store_dir, "dev") is False


def test_is_stale_true_when_ttl_elapsed(store_dir):
    set_ttl(store_dir, "dev", 1)
    # Backdate created_at so the TTL has already elapsed
    import json
    p = store_dir / ".ttl.json"
    data = json.loads(p.read_text())
    data["dev"]["created_at"] = time.time() - 10
    p.write_text(json.dumps(data))
    assert is_stale(store_dir, "dev") is True


def test_is_stale_false_when_no_ttl_set(store_dir):
    assert is_stale(store_dir, "dev") is False


def test_check_ttl_raises_when_stale(store_dir):
    import json
    set_ttl(store_dir, "dev", 1)
    p = store_dir / ".ttl.json"
    data = json.loads(p.read_text())
    data["dev"]["created_at"] = time.time() - 10
    p.write_text(json.dumps(data))
    with pytest.raises(TTLExpiredError):
        check_ttl(store_dir, "dev")


def test_check_ttl_does_not_raise_when_fresh(store_dir):
    set_ttl(store_dir, "dev", 3600)
    check_ttl(store_dir, "dev")  # should not raise


def test_clear_ttl_removes_entry(store_dir):
    set_ttl(store_dir, "dev", 3600)
    clear_ttl(store_dir, "dev")
    assert get_ttl(store_dir, "dev") is None


def test_clear_ttl_noop_when_not_set(store_dir):
    clear_ttl(store_dir, "nonexistent")  # should not raise


def test_list_ttl_returns_all_profiles(store_dir):
    set_ttl(store_dir, "dev", 3600)
    set_ttl(store_dir, "prod", 7200)
    rows = list_ttl(store_dir)
    names = {r["profile"] for r in rows}
    assert names == {"dev", "prod"}


def test_list_ttl_stale_flag(store_dir):
    import json
    set_ttl(store_dir, "old", 1)
    p = store_dir / ".ttl.json"
    data = json.loads(p.read_text())
    data["old"]["created_at"] = time.time() - 10
    p.write_text(json.dumps(data))
    rows = {r["profile"]: r for r in list_ttl(store_dir)}
    assert rows["old"]["stale"] is True
