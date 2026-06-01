from __future__ import annotations

import typer
from dotenv import find_dotenv, load_dotenv

from intervals_icu_cli.commands import activities, auth, events

app = typer.Typer(
    name="intervals-icu",
    help="Command-line interface for Intervals.icu.",
    no_args_is_help=True,
    add_completion=False,
)

app.add_typer(auth.app, name="auth")
app.add_typer(activities.app, name="activities")
app.add_typer(events.app, name="events")


@app.callback()
def main_callback() -> None:
    """Load a local .env (searched upward from the working directory) before running."""
    load_dotenv(find_dotenv(usecwd=True))


def main() -> None:
    """Entry point for the intervals-icu CLI."""
    app()


if __name__ == "__main__":
    main()
