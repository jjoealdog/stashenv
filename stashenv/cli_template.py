"""CLI commands for template rendering."""

import sys
from pathlib import Path

import click

from stashenv.store import load_profile
from stashenv.template import MissingVariableError, extract_variables, render_template, validate_template


@click.group("template")
def template_group():
    """Render .env templates with profile values as substitution variables."""


@template_group.command("render")
@click.argument("template_file", type=click.Path(exists=True, dir_okay=False))
@click.option("--profile", "-p", required=True, help="Profile whose values supply the variables.")
@click.option("--password", prompt=True, hide_input=True, help="Password to decrypt the profile.")
@click.option("--output", "-o", default=None, help="Write rendered output to this file (default: stdout).")
@click.option("--strict/--no-strict", default=True, show_default=True, help="Fail on unresolved placeholders.")
@click.option("--store-dir", default=None, hidden=True)
def render_cmd(template_file, profile, password, output, strict, store_dir):
    """Render TEMPLATE_FILE using variables from a named profile."""
    template_text = Path(template_file).read_text()

    warnings = validate_template(template_text)
    for w in warnings:
        click.echo(f"warning: {w}", err=True)

    kwargs = {"store_dir": store_dir} if store_dir else {}
    try:
        env_text = load_profile(profile, password, **kwargs)
    except FileNotFoundError:
        click.echo(f"error: profile '{profile}' not found.", err=True)
        sys.exit(1)
    except ValueError:
        click.echo("error: wrong password or corrupted profile.", err=True)
        sys.exit(1)

    variables = {}
    for line in env_text.splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        variables[key.strip()] = value.strip()

    try:
        rendered = render_template(template_text, variables, strict=strict)
    except MissingVariableError as exc:
        click.echo(f"error: {exc}", err=True)
        sys.exit(1)

    if output:
        Path(output).write_text(rendered)
        click.echo(f"Rendered template written to {output}")
    else:
        click.echo(rendered, nl=False)


@template_group.command("vars")
@click.argument("template_file", type=click.Path(exists=True, dir_okay=False))
def vars_cmd(template_file):
    """List all placeholder variables referenced in TEMPLATE_FILE."""
    template_text = Path(template_file).read_text()
    variables = extract_variables(template_text)
    if not variables:
        click.echo("No template variables found.")
    else:
        for v in variables:
            click.echo(v)


def register(cli):
    cli.add_command(template_group)
