"""Format (pretty-print / normalise) .env profile content."""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import List, Tuple


@dataclass
class FmtResult:
    original: str
    formatted: str
    changes: List[str] = field(default_factory=list)

    @property
    def changed(self) -> bool:
        return self.original != self.formatted


_COMMENT_RE = re.compile(r"^\s*#")
_BLANK_RE = re.compile(r"^\s*$")
_PAIR_RE = re.compile(r"^([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(.*)$")


def _strip_inline_comment(value: str) -> Tuple[str, str]:
    """Return (clean_value, inline_comment_or_empty)."""
    # Only strip unquoted inline comments
    if value.startswith(("'", '"')):
        return value, ""
    idx = value.find(" #")
    if idx == -1:
        return value, ""
    return value[:idx].rstrip(), "  " + value[idx:].lstrip()


def format_env_text(text: str, *, sort_keys: bool = False, strip_inline_comments: bool = False) -> FmtResult:
    """Normalise env text.

    Transformations applied:
    - Collapse multiple blank lines into one
    - Remove trailing whitespace from each line
    - Ensure KEY=value (no spaces around =)
    - Optionally sort keys alphabetically (comments/blanks stay at top)
    - Optionally strip inline comments
    """
    lines = text.splitlines()
    out: List[str] = []
    changes: List[str] = []
    prev_blank = False

    pairs: List[Tuple[str, str, str]] = []  # (key, value, comment)
    header: List[str] = []  # leading comment/blank block
    collecting_header = True

    for raw in lines:
        line = raw.rstrip()
        if _COMMENT_RE.match(line) or _BLANK_RE.match(line):
            if collecting_header:
                header.append(line)
            else:
                pairs.append(("", line, ""))  # sentinel for blank/comment
            continue
        m = _PAIR_RE.match(line)
        if m:
            collecting_header = False
            key, value = m.group(1), m.group(2)
            comment = ""
            if strip_inline_comments:
                value, comment = _strip_inline_comment(value)
                if comment:
                    changes.append(f"stripped inline comment from {key}")
            pairs.append((key, value, comment))
        else:
            collecting_header = False
            pairs.append(("", line, ""))  # non-matching passthrough

    if sort_keys:
        kv = [(k, v, c) for k, v, c in pairs if k and not k.startswith("#")]
        non_kv = [(k, v, c) for k, v, c in pairs if not k or k.startswith("#")]
        kv.sort(key=lambda t: t[0].lower())
        pairs = non_kv + kv
        changes.append("sorted keys alphabetically")

    for line in header:
        out.append(line)

    for key, value, comment in pairs:
        if not key:
            # blank line dedup
            if value == "":
                if not prev_blank:
                    out.append("")
                prev_blank = True
            else:
                out.append(value)
                prev_blank = False
        else:
            out.append(f"{key}={value}{comment}")
            prev_blank = False

    formatted = "\n".join(out)
    if not formatted.endswith("\n"):
        formatted += "\n"

    return FmtResult(original=text, formatted=formatted, changes=changes)
