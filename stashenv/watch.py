"""Watch a .env file for changes and auto-save to a named profile."""

import time
import os
from pathlib import Path
from typing import Callable, Optional


class WatchError(Exception):
    pass


class FileWatcher:
    """Watches a file for modifications and triggers a callback on change."""

    def __init__(
        self,
        path: str | Path,
        callback: Callable[[Path], None],
        interval: float = 1.0,
    ):
        self.path = Path(path)
        self.callback = callback
        self.interval = interval
        self._last_mtime: Optional[float] = None
        self._running = False

    def _get_mtime(self) -> Optional[float]:
        try:
            return self.path.stat().st_mtime
        except FileNotFoundError:
            return None

    def poll(self) -> bool:
        """Check once for changes. Returns True if a change was detected."""
        current = self._get_mtime()
        if current is None:
            return False
        if self._last_mtime is None:
            self._last_mtime = current
            return False
        if current != self._last_mtime:
            self._last_mtime = current
            self.callback(self.path)
            return True
        return False

    def start(self, max_iterations: Optional[int] = None) -> None:
        """Block and poll until stopped or max_iterations reached."""
        if not self.path.exists():
            raise WatchError(f"File not found: {self.path}")
        self._last_mtime = self._get_mtime()
        self._running = True
        iterations = 0
        while self._running:
            if max_iterations is not None and iterations >= max_iterations:
                break
            time.sleep(self.interval)
            self.poll()
            iterations += 1

    def stop(self) -> None:
        self._running = False


def watch_and_save(
    env_file: str | Path,
    profile: str,
    password: str,
    store_dir: Optional[Path] = None,
    interval: float = 1.0,
    max_iterations: Optional[int] = None,
) -> FileWatcher:
    """Create a FileWatcher that auto-saves env_file to profile on change."""
    from stashenv.store import save_profile

    env_file = Path(env_file)

    def _on_change(path: Path) -> None:
        content = path.read_text()
        save_profile(profile, content, password, store_dir=store_dir)

    watcher = FileWatcher(env_file, _on_change, interval=interval)
    return watcher
