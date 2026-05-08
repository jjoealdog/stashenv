"""Variable interpolation for env profiles.

Expands references like ${VAR} or $VAR within values using other keys
in the same profile or an optional extra context dict.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from stashenv.store import load_profile

_REF_RE = re.compile(r"\$\{([A-Za-z_][A-Za-z0-9_]*)\}|\$([A-Za-z_][A-Za-z0-9_]*)")


class UnresolvedVariableError(Exception):
    """Raised in strict mode when a referenced variable cannot be resolved."""


@dataclass
class InterpolateResult:
    expanded: dict[str, str]
    unresolved: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return len(self.unresolved) == 0


def _parse(text: str) -> dict[str, str]:
    out: dict[str, str] = {}
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if "=" not in stripped:
            continue
        k, _, v = stripped.partition("=")
        out[k.strip()] = v.strip()
    return out


def interpolate_text(
    text: str,
    context: Optional[dict[str, str]] = None,
    strict: bool = False,
) -> InterpolateResult:
    """Expand variable references within env text.

    Args:
        text: Raw .env file contents.
        context: Extra variables that take precedence over self-references.
        strict: If True raise UnresolvedVariableError for missing refs.

    Returns:
        InterpolateResult with expanded key/value pairs.
    """
    parsed = _parse(text)
    lookup = {**parsed, **(context or {})}
    expanded: dict[str, str] = {}
    unresolved: list[str] = []

    for key, value in parsed.items():
        def _replace(m: re.Match) -> str:
            ref = m.group(1) or m.group(2)
            if ref in lookup:
                return lookup[ref]
            unresolved.append(ref)
            if strict:
                raise UnresolvedVariableError(f"Variable '${ref}' could not be resolved")
            return m.group(0)

        expanded[key] = _REF_RE.sub(_replace, value)

    return InterpolateResult(expanded=expanded, unresolved=list(set(unresolved)))


def interpolate_profile(
    profile: str,
    password: str,
    store_dir: Path,
    context: Optional[dict[str, str]] = None,
    strict: bool = False,
) -> InterpolateResult:
    """Load a stored profile and interpolate its variables."""
    text = load_profile(profile, password, store_dir)
    return interpolate_text(text, context=context, strict=strict)
