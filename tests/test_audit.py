"""Tests for stashenv.audit."""

import pytest
from pathlib import Path

from stashenv.audit import record_event, read_events, clear_log


@pytest.fixture
def store_dir(tmp_path: Path) -> Path:
    return tmp_path / "store"


def test_record_creates_log_file(store_dir):
    record_event(store_dir, "load", "prod")
    assert (store_dir / ".audit.log").exists()


def test_read_events_empty_when_no_log(store_dir):
    assert read_events(store_dir) == []


def test_record_and_read_single_event(store_dir):
    record_event(store_dir, "save", "dev", success=True)
    events = read_events(store_dir)
    assert len(events) == 1
    assert events[0]["action"] == "save"
    assert events[0]["profile"] == "dev"
    assert events[0]["success"] is True


def test_multiple_events_appended_in_order(store_dir):
    record_event(store_dir, "save", "dev")
    record_event(store_dir, "load", "dev")
    record_event(store_dir, "delete", "dev", success=False)
    events = read_events(store_dir)
    assert len(events) == 3
    assert [e["action"] for e in events] == ["save", "load", "delete"]


def test_event_has_timestamp_and_pid(store_dir):
    record_event(store_dir, "load", "staging")
    event = read_events(store_dir)[0]
    assert "ts" in event
    assert "pid" in event
    assert isinstance(event["pid"], int)


def test_clear_log_removes_file(store_dir):
    record_event(store_dir, "load", "prod")
    clear_log(store_dir)
    assert not (store_dir / ".audit.log").exists()


def test_clear_log_no_error_when_missing(store_dir):
    # Should not raise even if log doesn't exist
    clear_log(store_dir)
