"""Mask sensitive values in .env profiles for safe display."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable

# Keys whose values are always masked regardless of user config
_DEFAULT_SENSITIVE_PATTERNS = (
    "SECRET",
    "PASSWORD",
    "PASSWD",
    "TOKEN",
    "API_KEY",
    "PRIVATE_KEY",
    "CREDENTIALS",
    "AUTH",
)

MASK_CHAR = "*"
MASK_LEN = 8


@dataclass
class MaskedLine:
    key: str
    raw_value: str
    masked_value: str
    is_masked: bool


def _is_sensitive(key: str, extra_patterns: Iterable[str] = ()) -> bool:
    upper = key.upper()
    for pattern in list(_DEFAULT_SENSITIVE_PATTERNS) + list(extra_patterns):
        if pattern.upper() in upper:
            return True
    return False


def _mask_value(value: str) -> str:
    if not value:
        return value
    if len(value) <= 4:
        return MASK_CHAR * MASK_LEN
    visible = value[:2]
    return visible + MASK_CHAR * (MASK_LEN - 2)


def mask_env_text(
    text: str,
    extra_patterns: Iterable[str] = (),
    show_keys: Iterable[str] = (),
) -> list[MaskedLine]:
    """Parse env text and return MaskedLine entries with sensitive values hidden."""
    results: list[MaskedLine] = []
    force_show = {k.upper() for k in show_keys}

    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip()
        sensitive = _is_sensitive(key, extra_patterns) and key.upper() not in force_show
        results.append(
            MaskedLine(
                key=key,
                raw_value=value,
                masked_value=_mask_value(value) if sensitive else value,
                is_masked=sensitive,
            )
        )
    return results


def format_masked(
    lines: list[MaskedLine],
    *,
    reveal: bool = False,
) -> str:
    """Format masked lines for terminal display."""
    rows = []
    for entry in lines:
        value = entry.raw_value if reveal else entry.masked_value
        indicator = " [masked]" if entry.is_masked and not reveal else ""
        rows.append(f"{entry.key}={value}{indicator}")
    return "\n".join(rows)
