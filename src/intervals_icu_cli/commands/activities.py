from __future__ import annotations

from datetime import date, timedelta
from typing import Optional

import typer

from intervals_icu_cli.commands._helpers import build_client, echo_json

app = typer.Typer(no_args_is_help=True, help="List and inspect activities.")


def _parse_date(value: Optional[str], fallback: date) -> date:
    if value is None:
        return fallback
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise typer.BadParameter(f"Invalid date '{value}', expected YYYY-MM-DD.") from exc


def _format_activity_line(activity: object) -> str:
    data = activity.to_dict() if hasattr(activity, "to_dict") else dict(activity)
    activity_id = data.get("id", "?")
    start = data.get("start_date_local") or data.get("start_date") or ""
    name = data.get("name") or "(unnamed)"
    activity_type = data.get("type") or ""
    return f"{activity_id}\t{start}\t{activity_type}\t{name}"


@app.command("list")
def list_activities(
    start: Optional[str] = typer.Option(
        None, "--start", help="Oldest date (YYYY-MM-DD). Defaults to 30 days ago."
    ),
    end: Optional[str] = typer.Option(
        None, "--end", help="Newest date (YYYY-MM-DD). Defaults to today."
    ),
    limit: int = typer.Option(50, "--limit", help="Maximum number of activities."),
    json_output: bool = typer.Option(
        False, "--json", help="Output raw JSON instead of a table."
    ),
) -> None:
    """List activities for the configured athlete."""
    today = date.today()
    start_date = _parse_date(start, today - timedelta(days=30))
    end_date = _parse_date(end, today)

    client = build_client()
    activities = client.list_activities(start=start_date, end=end_date, limit=limit)

    if json_output:
        echo_json(activities)
        return

    if not activities:
        typer.echo("No activities found.")
        return

    for activity in activities:
        typer.echo(_format_activity_line(activity))
