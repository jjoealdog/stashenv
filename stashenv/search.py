"""Search profiles by key name or value across the store."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from stashenv.store import list_profiles, load_profile
from stashenv.diff import parse_env_text


@dataclass
class SearchMatch:
    profile: str
    key: str
    value: str
    matched_on: str  # 'key' | 'value'


def search_profiles(
    store_dir: str,
    password: str,
    query: str,
    *,
    search_keys: bool = True,
    search_values: bool = False,
    case_sensitive: bool = False,
) -> list[SearchMatch]:
    """Search all profiles for keys/values matching *query*.

    Args:
        store_dir: Path to the stashenv store directory.
        password: Master password used to decrypt profiles.
        query: Substring to search for.
        search_keys: Include key-name matches.
        search_values: Include value matches.
        case_sensitive: Whether the match is case-sensitive.

    Returns:
        A list of :class:`SearchMatch` objects, one per matching key.
    """
    if not search_keys and not search_values:
        raise ValueError("At least one of search_keys or search_values must be True.")

    needle = query if case_sensitive else query.lower()
    matches: list[SearchMatch] = []

    for profile_name in list_profiles(store_dir):
        try:
            raw = load_profile(store_dir, profile_name, password)
        except Exception:
            # Skip profiles that cannot be decrypted with the given password.
            continue

        env_vars = parse_env_text(raw)

        for key, value in env_vars.items():
            haystack_key = key if case_sensitive else key.lower()
            haystack_val = value if case_sensitive else value.lower()

            if search_keys and needle in haystack_key:
                matches.append(SearchMatch(profile=profile_name, key=key, value=value, matched_on="key"))
            elif search_values and needle in haystack_val:
                matches.append(SearchMatch(profile=profile_name, key=key, value=value, matched_on="value"))

    return matches


def format_search_results(matches: list[SearchMatch], *, show_values: bool = False) -> str:
    """Render search results as a human-readable string."""
    if not matches:
        return "No matches found."

    lines: list[str] = []
    current_profile: Optional[str] = None

    for m in sorted(matches, key=lambda x: (x.profile, x.key)):
        if m.profile != current_profile:
            lines.append(f"\n[{m.profile}]")
            current_profile = m.profile
        if show_values:
            lines.append(f"  {m.key} = {m.value}  ({m.matched_on})")
        else:
            lines.append(f"  {m.key}  ({m.matched_on})")

    return "\n".join(lines).lstrip()
