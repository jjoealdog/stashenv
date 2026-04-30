"""Lint .env profiles for common issues."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List

from stashenv.store import load_profile, list_profiles


@dataclass
class LintIssue:
    line: int
    key: str
    message: str
    severity: str  # 'warning' | 'error'


@dataclass
class LintResult:
    profile: str
    issues: List[LintIssue] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not any(i.severity == "error" for i in self.issues)


def _parse_lines(text: str):
    """Yield (line_number, raw_line) for non-blank, non-comment lines."""
    for i, line in enumerate(text.splitlines(), start=1):
        stripped = line.strip()
        if stripped and not stripped.startswith("#"):
            yield i, line


def lint_text(profile: str, text: str) -> LintResult:
    result = LintResult(profile=profile)
    seen_keys: dict[str, int] = {}

    for lineno, line in _parse_lines(text):
        if "=" not in line:
            result.issues.append(
                LintIssue(lineno, "", "Line has no '=' separator", "error")
            )
            continue

        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip()

        if not key:
            result.issues.append(
                LintIssue(lineno, key, "Empty key", "error")
            )
        elif " " in key:
            result.issues.append(
                LintIssue(lineno, key, f"Key '{key}' contains whitespace", "error")
            )
        elif not key[0].isalpha() and key[0] != "_":
            result.issues.append(
                LintIssue(lineno, key, f"Key '{key}' starts with invalid character", "warning")
            )

        if key in seen_keys:
            result.issues.append(
                LintIssue(lineno, key, f"Duplicate key '{key}' (first seen on line {seen_keys[key]})", "warning")
            )
        else:
            seen_keys[key] = lineno

        if not value:
            result.issues.append(
                LintIssue(lineno, key, f"Key '{key}' has an empty value", "warning")
            )

    return result


def lint_profile(store_dir, profile: str, password: str) -> LintResult:
    text = load_profile(store_dir, profile, password)
    return lint_text(profile, text)


def lint_all_profiles(store_dir, password: str) -> List[LintResult]:
    return [lint_profile(store_dir, p, password) for p in list_profiles(store_dir)]
