"""Tests for stashenv/expire.py"""

import pytest
from datetime import datetime, timedelta, timezone
from pathlib import Path

from stashenv.expire import (
    set_expiry,
    clear_expiry,
    get_expiry,
    check_expiry,
    list_expiry,
    ProfileExpiredError,
)


@pytest.fixture
def store_dir(tmp_path):
    return tmp_path


def _future(days=1):
    return datetime.now(timezone.utc) + timedelta(days=days)


def _past(days=1):
    return datetime.now(timezone.utc) - timedelta(days=days)


def test_get_expiry_returns_none_when_no_file(store_dir):
    assert get_expiry(store_dir, "dev") is None


def test_set_expiry_creates_file(store_dir):
    set_expiry(store_dir, "dev", _future())
    assert (store_dir / ".expiry.json").exists()


def test_set_and_get_expiry_roundtrip(store_dir):
    expires = _future(3)
    set_expiry(store_dir, "dev", expires)
    result = get_expiry(store_dir, "dev")
    assert result is not None
    assert abs((result - expires).total_seconds()) < 1


def test_check_expiry_passes_for_future(store_dir):
    set_expiry(store_dir, "dev", _future())
    check_expiry(store_dir, "dev")  # should not raise


def test_check_expiry_raises_for_past(store_dir):
    set_expiry(store_dir, "dev", _past())
    with pytest.raises(ProfileExpiredError, match="dev"):
        check_expiry(store_dir, "dev")


def test_check_expiry_no_expiry_set_passes(store_dir):
    check_expiry(store_dir, "dev")  # should not raise


def test_clear_expiry_removes_entry(store_dir):
    set_expiry(store_dir, "dev", _future())
    removed = clear_expiry(store_dir, "dev")
    assert removed is True
    assert get_expiry(store_dir, "dev") is None


def test_clear_expiry_returns_false_when_not_set(store_dir):
    assert clear_expiry(store_dir, "dev") is False


def test_list_expiry_returns_all(store_dir):
    set_expiry(store_dir, "dev", _future(1))
    set_expiry(store_dir, "prod", _future(7))
    result = list_expiry(store_dir)
    assert set(result.keys()) == {"dev", "prod"}
    assert isinstance(result["dev"], datetime)


def test_list_expiry_empty_when_no_file(store_dir):
    assert list_expiry(store_dir) == {}


def test_set_expiry_overwrites_existing(store_dir):
    set_expiry(store_dir, "dev", _future(1))
    new_expiry = _future(10)
    set_expiry(store_dir, "dev", new_expiry)
    result = get_expiry(store_dir, "dev")
    assert abs((result - new_expiry).total_seconds()) < 1
