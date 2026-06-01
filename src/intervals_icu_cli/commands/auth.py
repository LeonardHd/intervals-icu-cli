from __future__ import annotations

import os
import sys
from typing import Optional

import typer

from intervals_icu_cli.config import (
    DEFAULT_BASE_URL,
    config_path,
    delete_config_file,
    read_config_file,
    write_config_file,
)

app = typer.Typer(
    no_args_is_help=True, help="Manage stored Intervals.icu credentials."
)


def _mask(secret: str) -> str:
    if len(secret) <= 4:
        return "***"
    return f"{secret[:4]}...{secret[-2:]}"


@app.command("login")
def login(
    athlete_id: Optional[str] = typer.Option(
        None, "--athlete-id", help="Athlete ID, e.g. i12345."
    ),
    api_key: Optional[str] = typer.Option(
        None, "--api-key", help="API key. Pass '-' to read it from stdin."
    ),
    base_url: Optional[str] = typer.Option(
        None, "--base-url", help=f"Base URL. Defaults to {DEFAULT_BASE_URL}."
    ),
) -> None:
    """Store credentials in the config file.

    Provide --athlete-id and --api-key for non-interactive (headless) use. When
    a value is omitted and a terminal is attached, you are prompted for it;
    without a terminal the command fails instead of hanging.
    """
    if api_key == "-":
        api_key = sys.stdin.readline().strip()

    interactive = sys.stdin.isatty()

    if athlete_id is None:
        if interactive:
            athlete_id = typer.prompt("Athlete ID")
        else:
            raise typer.BadParameter(
                "Provide --athlete-id (no terminal available to prompt)."
            )

    if api_key is None:
        if interactive:
            api_key = typer.prompt("API key", hide_input=True)
        else:
            raise typer.BadParameter(
                "Provide --api-key (no terminal available to prompt)."
            )

    path = write_config_file(
        athlete_id=athlete_id, api_key=api_key, base_url=base_url
    )
    typer.echo(f"Saved credentials to {path}")


@app.command("status")
def status() -> None:
    """Show how credentials currently resolve, without making a network call."""
    file_data = read_config_file()

    env_athlete = os.getenv("INTERVALS_ICU_ATHLETE_ID")
    env_key = os.getenv("INTERVALS_ICU_API_KEY")

    athlete_id = env_athlete or file_data.get("athlete_id")
    api_key = env_key or file_data.get("api_key")

    if not athlete_id or not api_key:
        typer.echo(
            "Not authenticated. Set INTERVALS_ICU_ATHLETE_ID and "
            "INTERVALS_ICU_API_KEY, or run 'intervals-icu auth login'."
        )
        raise typer.Exit(code=1)

    athlete_source = "env" if env_athlete else "config file"
    key_source = "env" if env_key else "config file"

    typer.echo(f"Athlete ID:  {athlete_id} (from {athlete_source})")
    typer.echo(f"API key:     {_mask(api_key)} (from {key_source})")
    typer.echo(f"Config file: {config_path()}")


@app.command("logout")
def logout() -> None:
    """Delete the stored credentials config file."""
    if delete_config_file():
        typer.echo(f"Removed {config_path()}")
    else:
        typer.echo("No stored credentials to remove.")
