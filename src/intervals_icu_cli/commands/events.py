from __future__ import annotations

import json
import sys
from datetime import date, datetime, timedelta
from typing import Optional

import typer

from intervals_icu_cli.commands._helpers import build_client, echo_json
from intervals_icu_cli.mapper import map_event_create_request_to_intervals_api
from intervals_icu_cli.models import (
    EventCategory,
    EventCreateRequest,
    EventCreateResponse,
    WorkoutType,
)
from intervals_icu_cli.workout_models import Workout

app = typer.Typer(no_args_is_help=True, help="List, create, and delete calendar events.")


def _format_event_line(event: object) -> str:
    data = event.to_dict() if hasattr(event, "to_dict") else dict(event)
    event_id = data.get("id", "?")
    start = data.get("start_date_local") or data.get("start_date") or ""
    category = data.get("category") or ""
    name = data.get("name") or "(unnamed)"
    return f"{event_id}\t{start}\t{category}\t{name}"


@app.command("list")
def list_events(
    oldest_days_ago: int = typer.Option(
        30, "--oldest-days-ago", help="How many days back to include."
    ),
    newest_days_ahead: int = typer.Option(
        30, "--newest-days-ahead", help="How many days ahead to include."
    ),
    category: Optional[str] = typer.Option(
        "WORKOUT", "--category", help="Event category filter."
    ),
    limit: int = typer.Option(50, "--limit", help="Maximum number of events."),
    json_output: bool = typer.Option(
        False, "--json", help="Output raw JSON instead of a table."
    ),
) -> None:
    """List planned events for the configured athlete."""
    today = date.today()
    oldest = today - timedelta(days=oldest_days_ago)
    newest = today + timedelta(days=newest_days_ahead)

    client = build_client()
    events = client.list_events(
        oldest=oldest, newest=newest, category=category, limit=limit
    )

    if json_output:
        echo_json(events)
        return

    if not events:
        typer.echo("No events found.")
        return

    for event in events:
        typer.echo(_format_event_line(event))


@app.command("create")
def create_event(
    name: str = typer.Option(..., "--name", help="Event name."),
    date_arg: str = typer.Option(
        ..., "--date", help="ISO datetime, e.g. 2025-12-04T07:00:00."
    ),
    file: Optional[str] = typer.Option(
        None,
        "--file",
        "-f",
        help="Path to a workout JSON file. Reads stdin if omitted.",
    ),
    type: Optional[WorkoutType] = typer.Option(
        None, "--type", help="Workout type, e.g. Run, Ride, Swim."
    ),
    category: EventCategory = typer.Option(
        EventCategory.WORKOUT, "--category", help="Event category."
    ),
    description: Optional[str] = typer.Option(
        None, "--description", help="Additional description text."
    ),
    json_output: bool = typer.Option(
        False, "--json", help="Output raw JSON instead of a summary."
    ),
) -> None:
    """Create a calendar event from a structured workout definition.

    The workout JSON must be an object with a "steps" array. See the SKILL.md
    for the full schema and examples.
    """
    raw = _read_workout_source(file)
    try:
        workout_data = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise typer.BadParameter(f"Invalid workout JSON: {exc}") from exc

    try:
        event_datetime = datetime.fromisoformat(date_arg)
    except ValueError as exc:
        raise typer.BadParameter(
            f"Invalid date '{date_arg}', expected ISO datetime."
        ) from exc

    request = EventCreateRequest(
        name=name,
        date=event_datetime,
        workout=Workout.model_validate(workout_data),
        category=category,
        type=type,
        description=description,
    )
    event_ex = map_event_create_request_to_intervals_api(request)

    client = build_client()
    created = client.create_event(event_ex)

    response = EventCreateResponse(
        id=int(created.id or 0),
        name=created.name or "",
        date=created.start_date_local or "",
        description=created.description or "",
    )

    if json_output:
        echo_json(response.model_dump())
        return

    typer.echo(f"Created event {response.id}: {response.name} ({response.date})")


@app.command("delete")
def delete_event(
    event_id: int = typer.Argument(..., help="ID of the event to delete."),
) -> None:
    """Delete a calendar event by ID."""
    client = build_client()
    client.delete_event(event_id=event_id)
    typer.echo(f"Event {event_id} deleted successfully")


def _read_workout_source(file: Optional[str]) -> str:
    if file is None or file == "-":
        return sys.stdin.read()
    with open(file, "r", encoding="utf-8") as handle:
        return handle.read()
