"""Sort keys in a .env profile alphabetically or by custom order."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional


@dataclass
class SortResult:
    profile: str
    changed: bool
    original_order: List[str]
    sorted_order: List[str]


def _parse_lines(text: str):
    """Return list of (key, raw_line) tuples preserving comments/blanks as (None, raw_line)."""
    entries = []
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            entries.append((None, line))
        elif "=" in stripped:
            key = stripped.split("=", 1)[0].strip()
            entries.append((key, line))
        else:
            entries.append((None, line))
    return entries


def sort_env_text(
    text: str,
    reverse: bool = False,
    group_comments: bool = True,
) -> str:
    """Return env text with key=value lines sorted alphabetically.

    Comments immediately preceding a key are kept attached to that key
    when group_comments=True (default). Blank lines between groups are
    preserved as section separators.
    """
    lines = text.splitlines()
    # Split into sections divided by blank lines
    sections: List[List[str]] = []
    current: List[str] = []
    for line in lines:
        if line.strip() == "":
            if current:
                sections.append(current)
                current = []
            sections.append([""])
        else:
            current.append(line)
    if current:
        sections.append(current)

    sorted_sections = []
    for section in sections:
        if len(section) == 1 and section[0] == "":
            sorted_sections.append(section)
            continue

        # Group lines: attach leading comments to the next key line
        groups: List[List[str]] = []
        pending_comments: List[str] = []
        for line in section:
            stripped = line.strip()
            if stripped.startswith("#"):
                if group_comments:
                    pending_comments.append(line)
                else:
                    groups.append([line])
            elif "=" in stripped:
                block = pending_comments + [line]
                pending_comments = []
                groups.append(block)
            else:
                if pending_comments:
                    groups.extend([[c] for c in pending_comments])
                    pending_comments = []
                groups.append([line])
        if pending_comments:
            groups.extend([[c] for c in pending_comments])

        def sort_key(block: List[str]) -> str:
            for ln in reversed(block):
                if "=" in ln and not ln.strip().startswith("#"):
                    return ln.strip().split("=", 1)[0].strip().lower()
            return "\x00"  # comments/unknowns sort first

        groups.sort(key=sort_key, reverse=reverse)
        sorted_sections.append([ln for block in groups for ln in block])

    result_lines = [ln for section in sorted_sections for ln in section]
    return "\n".join(result_lines)


def sort_profile(
    profile: str,
    store_dir: Path,
    password: str,
    reverse: bool = False,
) -> SortResult:
    """Load, sort, and re-save a profile. Returns a SortResult."""
    from stashenv.store import load_profile, save_profile

    original_text = load_profile(profile, store_dir, password)
    sorted_text = sort_env_text(original_text, reverse=reverse)

    original_keys = [
        ln.split("=", 1)[0].strip()
        for ln in original_text.splitlines()
        if "=" in ln and not ln.strip().startswith("#")
    ]
    sorted_keys = [
        ln.split("=", 1)[0].strip()
        for ln in sorted_text.splitlines()
        if "=" in ln and not ln.strip().startswith("#")
    ]

    changed = original_text != sorted_text
    if changed:
        save_profile(profile, store_dir, sorted_text, password)

    return SortResult(
        profile=profile,
        changed=changed,
        original_order=original_keys,
        sorted_order=sorted_keys,
    )
