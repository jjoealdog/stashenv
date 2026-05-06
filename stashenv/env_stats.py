"""Compute statistics about a profile's env contents."""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class EnvStats:
    profile: str
    total_keys: int = 0
    empty_values: int = 0
    comment_lines: int = 0
    blank_lines: int = 0
    duplicate_keys: List[str] = field(default_factory=list)
    longest_key: str = ""
    longest_value_key: str = ""
    avg_value_length: float = 0.0


def compute_stats(profile: str, text: str) -> EnvStats:
    """Analyse *text* (raw .env content) and return an EnvStats instance."""
    stats = EnvStats(profile=profile)
    seen: Dict[str, int] = {}
    value_lengths: List[int] = []
    max_key_len = 0
    max_val_len = -1

    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            stats.blank_lines += 1
            continue
        if line.startswith("#"):
            stats.comment_lines += 1
            continue
        if "=" not in line:
            continue

        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip()

        stats.total_keys += 1
        seen[key] = seen.get(key, 0) + 1

        if not value:
            stats.empty_values += 1

        if len(key) > max_key_len:
            max_key_len = len(key)
            stats.longest_key = key

        if len(value) > max_val_len:
            max_val_len = len(value)
            stats.longest_value_key = key

        value_lengths.append(len(value))

    stats.duplicate_keys = [k for k, count in seen.items() if count > 1]
    if value_lengths:
        stats.avg_value_length = sum(value_lengths) / len(value_lengths)

    return stats


def format_stats(stats: EnvStats) -> str:
    """Return a human-readable summary of *stats*."""
    dupes = ", ".join(stats.duplicate_keys) if stats.duplicate_keys else "none"
    lines = [
        f"Profile : {stats.profile}",
        f"Keys    : {stats.total_keys}",
        f"Empty   : {stats.empty_values}",
        f"Comments: {stats.comment_lines}",
        f"Blanks  : {stats.blank_lines}",
        f"Dupes   : {dupes}",
        f"Longest key  : {stats.longest_key or '-'}",
        f"Longest value: {stats.longest_value_key or '-'}",
        f"Avg val len  : {stats.avg_value_length:.1f}",
    ]
    return "\n".join(lines)
