"""Profile validation: check env values against regex or allowed-values rules."""
from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


@dataclass
class ValidationRule:
    key: str
    pattern: Optional[str] = None          # regex the value must match
    allowed: Optional[list[str]] = None    # explicit allowed values
    required: bool = True


@dataclass
class ValidationIssue:
    key: str
    message: str
    is_error: bool = True


@dataclass
class ValidationResult:
    issues: list[ValidationIssue] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not any(i.is_error for i in self.issues)


def _rules_path(store_dir: Path, profile: str) -> Path:
    return store_dir / f"{profile}.rules.json"


def save_rules(store_dir: Path, profile: str, rules: list[ValidationRule]) -> None:
    path = _rules_path(store_dir, profile)
    data = [
        {k: v for k, v in {
            "key": r.key,
            "pattern": r.pattern,
            "allowed": r.allowed,
            "required": r.required,
        }.items() if v is not None}
        for r in rules
    ]
    path.write_text(json.dumps(data, indent=2))


def load_rules(store_dir: Path, profile: str) -> list[ValidationRule]:
    path = _rules_path(store_dir, profile)
    if not path.exists():
        return []
    raw = json.loads(path.read_text())
    return [ValidationRule(**entry) for entry in raw]


def validate_env(env: dict[str, str], rules: list[ValidationRule]) -> ValidationResult:
    result = ValidationResult()
    for rule in rules:
        if rule.key not in env:
            if rule.required:
                result.issues.append(ValidationIssue(rule.key, "required key is missing"))
            continue
        value = env[rule.key]
        if rule.pattern and not re.fullmatch(rule.pattern, value):
            result.issues.append(
                ValidationIssue(rule.key, f"value {value!r} does not match pattern {rule.pattern!r}")
            )
        if rule.allowed is not None and value not in rule.allowed:
            result.issues.append(
                ValidationIssue(rule.key, f"value {value!r} not in allowed list {rule.allowed}")
            )
    return result
