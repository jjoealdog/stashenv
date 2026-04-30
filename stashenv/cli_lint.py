"""CLI commands for linting .env profiles."""
import click

from stashenv.lint import lint_profile, lint_all_profiles
from stashenv.store import list_profiles


@click.group("lint")
def lint_group():
    """Check profiles for common .env issues."""


def _print_result(result, show_values: bool = False) -> int:
    """Print lint result, return exit code (0 = clean, 1 = issues)."""
    if not result.issues:
        click.echo(click.style(f"✔  {result.profile}: no issues", fg="green"))
        return 0

    click.echo(click.style(f"✘  {result.profile}:", fg="red" if not result.ok else "yellow"))
    for issue in result.issues:
        colour = "red" if issue.severity == "error" else "yellow"
        tag = issue.severity.upper()
        key_part = f" [{issue.key}]" if issue.key else ""
        click.echo(
            click.style(f"   line {issue.line:>3}{key_part}  [{tag}] {issue.message}", fg=colour)
        )
    return 0 if result.ok else 1


@lint_group.command("run")
@click.argument("profile")
@click.option("--password", "-p", prompt=True, hide_input=True)
@click.pass_context
def run_cmd(ctx, profile: str, password: str):
    """Lint a single profile."""
    store_dir = ctx.obj["store_dir"]
    try:
        result = lint_profile(store_dir, profile, password)
    except FileNotFoundError:
        click.echo(f"Profile '{profile}' not found.", err=True)
        ctx.exit(1)
        return
    code = _print_result(result)
    ctx.exit(code)


@lint_group.command("all")
@click.option("--password", "-p", prompt=True, hide_input=True)
@click.pass_context
def all_cmd(ctx, password: str):
    """Lint all profiles in the store."""
    store_dir = ctx.obj["store_dir"]
    profiles = list_profiles(store_dir)
    if not profiles:
        click.echo("No profiles found.")
        return

    exit_code = 0
    for name in profiles:
        try:
            result = lint_profile(store_dir, name, password)
            code = _print_result(result)
            if code != 0:
                exit_code = code
        except Exception as exc:  # noqa: BLE001
            click.echo(click.style(f"  {name}: error — {exc}", fg="red"), err=True)
            exit_code = 1

    ctx.exit(exit_code)


def register(cli):
    cli.add_command(lint_group)
