import sys
import click
from stashenv.store import save_profile, load_profile, list_profiles, delete_profile


@click.group()
def cli():
    """stashenv — securely store and switch between named .env profiles."""
    pass


@cli.command("save")
@click.argument("profile_name")
@click.option("--password", prompt=True, hide_input=True, confirmation_prompt=True,
              help="Password to encrypt the profile.")
@click.option("--env-file", default=".env", show_default=True,
              help="Path to the .env file to save.")
def save(profile_name, password, env_file):
    """Save a .env file as a named profile."""
    try:
        with open(env_file, "rb") as f:
            plaintext = f.read()
    except FileNotFoundError:
        click.echo(f"Error: file '{env_file}' not found.", err=True)
        sys.exit(1)

    save_profile(profile_name, plaintext, password)
    click.echo(f"Profile '{profile_name}' saved.")


@cli.command("load")
@click.argument("profile_name")
@click.option("--password", prompt=True, hide_input=True,
              help="Password to decrypt the profile.")
@click.option("--env-file", default=".env", show_default=True,
              help="Destination path to write the .env file.")
def load(profile_name, password, env_file):
    """Load a named profile and write it to a .env file."""
    try:
        plaintext = load_profile(profile_name, password)
    except FileNotFoundError:
        click.echo(f"Error: profile '{profile_name}' does not exist.", err=True)
        sys.exit(1)
    except ValueError:
        click.echo("Error: wrong password or corrupted profile.", err=True)
        sys.exit(1)

    with open(env_file, "wb") as f:
        f.write(plaintext)
    click.echo(f"Profile '{profile_name}' loaded into '{env_file}'.")


@cli.command("list")
def list_cmd():
    """List all saved profiles for the current project."""
    profiles = list_profiles()
    if not profiles:
        click.echo("No profiles saved yet.")
    else:
        click.echo("Saved profiles:")
        for name in profiles:
            click.echo(f"  - {name}")


@cli.command("delete")
@click.argument("profile_name")
@click.confirmation_option(prompt="Are you sure you want to delete this profile?")
def delete(profile_name):
    """Delete a named profile."""
    try:
        delete_profile(profile_name)
        click.echo(f"Profile '{profile_name}' deleted.")
    except FileNotFoundError:
        click.echo(f"Error: profile '{profile_name}' does not exist.", err=True)
        sys.exit(1)


if __name__ == "__main__":
    cli()
