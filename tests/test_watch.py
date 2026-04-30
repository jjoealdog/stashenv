"""Tests for stashenv.watch"""

import time
import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch, call

from stashenv.watch import FileWatcher, WatchError, watch_and_save


@pytest.fixture
def env_file(tmp_path):
    f = tmp_path / ".env"
    f.write_text("KEY=value\n")
    return f


def test_poll_returns_false_on_first_call(env_file):
    cb = MagicMock()
    watcher = FileWatcher(env_file, cb)
    result = watcher.poll()
    assert result is False
    cb.assert_not_called()


def test_poll_detects_change(env_file):
    cb = MagicMock()
    watcher = FileWatcher(env_file, cb)
    watcher.poll()  # seed mtime
    # Bump mtime manually
    env_file.write_text("KEY=changed\n")
    # Force a different mtime
    new_time = env_file.stat().st_mtime + 1
    import os
    os.utime(env_file, (new_time, new_time))
    result = watcher.poll()
    assert result is True
    cb.assert_called_once_with(env_file)


def test_poll_no_change_does_not_call_callback(env_file):
    cb = MagicMock()
    watcher = FileWatcher(env_file, cb)
    watcher.poll()
    watcher.poll()
    cb.assert_not_called()


def test_poll_missing_file_returns_false(tmp_path):
    missing = tmp_path / "ghost.env"
    cb = MagicMock()
    watcher = FileWatcher(missing, cb)
    assert watcher.poll() is False


def test_start_raises_when_file_missing(tmp_path):
    missing = tmp_path / "nope.env"
    watcher = FileWatcher(missing, MagicMock(), interval=0)
    with pytest.raises(WatchError, match="File not found"):
        watcher.start(max_iterations=0)


def test_start_stops_after_max_iterations(env_file):
    cb = MagicMock()
    watcher = FileWatcher(env_file, cb, interval=0)
    watcher.start(max_iterations=3)
    assert not watcher._running


def test_stop_sets_running_false(env_file):
    cb = MagicMock()
    watcher = FileWatcher(env_file, cb)
    watcher._running = True
    watcher.stop()
    assert watcher._running is False


def test_watch_and_save_calls_save_on_change(tmp_path, env_file):
    store_dir = tmp_path / "store"
    store_dir.mkdir()

    with patch("stashenv.watch.save_profile") as mock_save:
        watcher = watch_and_save(
            env_file,
            profile="dev",
            password="secret",
            store_dir=store_dir,
            interval=0,
        )
        # Seed the mtime
        watcher.poll()
        # Simulate file change
        env_file.write_text("KEY=new\n")
        import os
        new_time = env_file.stat().st_mtime + 1
        os.utime(env_file, (new_time, new_time))
        watcher.poll()

    mock_save.assert_called_once_with("dev", "KEY=new\n", "secret", store_dir=store_dir)
