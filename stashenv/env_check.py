"""Validate .env profiles against a required keys schema."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable


@dataclass
class CheckResult:
    profile: str
    missing: list[str] = field(default_factory=list)
    extra: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.missing


def load_required_keys(schema_path: Path) -> list[str]:
    """Read a plain-text file with one required key per line."""
    keys: list[str] = []
    for line in schema_path.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#"):
            keys.append(line)
    return keys


def check_profile(profile_name: str, env_text: str, required_keys: Iterable[str]) -> CheckResult:
    """Compare keys present in *env_text* against *required_keys*."""
    required = set(required_keys)
    present: set[str] = set()

    for line in env_text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" in line:
            key = line.split("=", 1)[0].strip()
            present.add(key)

    missing = sorted(required - present)
    extra = sorted(present - required)
    return CheckResult(profile=profile_name, missing=missing, extra=extra)


def format_check_result(result: CheckResult) -> str:
    lines: list[str] = []
    status = "OK" if result.ok else "FAIL"
    lines.append(f"[{status}] {result.profile}")
    for key in result.missing:
        lines.append(f"  MISSING  {key}")
    for key in result.extra:
        lines.append(f"  EXTRA    {key}")
    return "\n".join(lines)
