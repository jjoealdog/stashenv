"""CLI commands for managing and running profile validation rules."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import click

from stashenv.store import _store_dir, load_profile
from stashenv.validate import (
    ValidationRule,
    load_rules,
    save_rules,
    validate_env,
)


@click.group("validate")
def validate_group() -> None:
    """Validate profile values against defined rules."""


@validate_group.command("run")
@click.argument("profile")
@click.password_option(prompt="Password", confirmation_prompt=False)
@click.option("--store", "store_path", default=None, help="Custom store directory.")
def run_cmd(profile: str, password: str, store_path: str | None) -> None:
    """Validate PROFILE against its saved rules."""
    store = Path(store_path) if store_path else _store_dir()
    try:
        raw = load_profile(profile, password, store)
    except Exception as exc:
        click.echo(f"Error loading profile: {exc}", err=True)
        sys.exit(1)

    env = dict(
        line.split("=", 1)
        for line in raw.splitlines()
        if "=" in line and not line.startswith("#")
    )
    rules = load_rules(store, profile)
    if not rules:
        click.echo("No rules defined for this profile.")
        return

    result = validate_env(env, rules)
    if result.ok:
        click.echo(f"✓ Profile '{profile}' passed all validation rules.")
    else:
        for issue in result.issues:
            level = "ERROR" if issue.is_error else "WARN"
            click.echo(f"  [{level}] {issue.key}: {issue.message}")
        sys.exit(1)


@validate_group.command("add-rule")
@click.argument("profile")
@click.argument("key")
@click.option("--pattern", default=None, help="Regex pattern the value must match.")
@click.option("--allowed", default=None, help="Comma-separated list of allowed values.")
@click.option("--optional", is_flag=True, default=False, help="Mark key as optional.")
@click.option("--store", "store_path", default=None)
def add_rule_cmd(
    profile: str,
    key: str,
    pattern: str | None,
    allowed: str | None,
    optional: bool,
    store_path: str | None,
) -> None:
    """Add a validation rule for KEY in PROFILE."""
    store = Path(store_path) if store_path else _store_dir()
    rules = load_rules(store, profile)
    allowed_list = [v.strip() for v in allowed.split(",")] if allowed else None
    rules.append(ValidationRule(key=key, pattern=pattern, allowed=allowed_list, required=not optional))
    save_rules(store, profile, rules)
    click.echo(f"Rule added for '{key}' in profile '{profile}'.")


@validate_group.command("list-rules")
@click.argument("profile")
@click.option("--store", "store_path", default=None)
def list_rules_cmd(profile: str, store_path: str | None) -> None:
    """List validation rules for PROFILE."""
    store = Path(store_path) if store_path else _store_dir()
    rules = load_rules(store, profile)
    if not rules:
        click.echo("No rules defined.")
        return
    for r in rules:
        parts = [r.key]
        if r.pattern:
            parts.append(f"pattern={r.pattern!r}")
        if r.allowed:
            parts.append(f"allowed={r.allowed}")
        parts.append("optional" if not r.required else "required")
        click.echo("  " + "  ".join(parts))


def register(cli: click.Group) -> None:
    cli.add_command(validate_group)
