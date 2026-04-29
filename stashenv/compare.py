"""Compare two profiles side-by-side, showing keys and values from both."""

from dataclasses import dataclass
from typing import Optional
from stashenv.store import load_profile
from stashenv.diff import parse_env_text


@dataclass
class CompareRow:
    key: str
    left_value: Optional[str]
    right_value: Optional[str]

    @property
    def is_same(self) -> bool:
        return self.left_value == self.right_value

    @property
    def status(self) -> str:
        if self.left_value is None:
            return "added"
        if self.right_value is None:
            return "removed"
        if self.left_value != self.right_value:
            return "changed"
        return "same"


def compare_profiles(
    store_dir,
    left_name: str,
    right_name: str,
    password: str,
) -> list[CompareRow]:
    """Load two profiles and produce a full side-by-side comparison."""
    left_text = load_profile(store_dir, left_name, password)
    right_text = load_profile(store_dir, right_name, password)

    left_vars = parse_env_text(left_text)
    right_vars = parse_env_text(right_text)

    all_keys = sorted(set(left_vars) | set(right_vars))

    return [
        CompareRow(
            key=key,
            left_value=left_vars.get(key),
            right_value=right_vars.get(key),
        )
        for key in all_keys
    ]


def format_compare(
    rows: list[CompareRow],
    left_name: str,
    right_name: str,
    show_values: bool = False,
    only_differences: bool = False,
) -> str:
    """Render a compare result as a human-readable table string."""
    if only_differences:
        rows = [r for r in rows if not r.is_same]

    if not rows:
        return f"  No differences between '{left_name}' and '{right_name}'."

    key_w = max(len(r.key) for r in rows)
    col_w = 30 if show_values else 10
    header = f"  {'KEY':<{key_w}}  {left_name[:col_w]:<{col_w}}  {right_name[:col_w]:<{col_w}}  STATUS"
    sep = "  " + "-" * (key_w + col_w * 2 + 14)
    lines = [header, sep]

    for row in rows:
        if show_values:
            lv = (row.left_value or "")[:col_w]
            rv = (row.right_value or "")[:col_w]
        else:
            lv = "<set>" if row.left_value is not None else "<missing>"
            rv = "<set>" if row.right_value is not None else "<missing>"

        lines.append(f"  {row.key:<{key_w}}  {lv:<{col_w}}  {rv:<{col_w}}  {row.status}")

    return "\n".join(lines)
