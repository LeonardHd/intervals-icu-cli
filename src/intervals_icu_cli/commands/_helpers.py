from __future__ import annotations

import json
from typing import Any

import typer

from intervals_icu_cli.client import (
    IntervalsAuthError,
    IntervalsClient,
    get_intervals_client,
)


def build_client() -> IntervalsClient:
    """Build an IntervalsClient, exiting with a clear message if auth is missing."""
    try:
        return get_intervals_client()
    except IntervalsAuthError as exc:
        typer.secho(str(exc), fg=typer.colors.RED, err=True)
        raise typer.Exit(code=1)


def to_serializable(obj: Any) -> Any:
    """Recursively convert SDK models (with to_dict) into JSON-serializable data."""
    if hasattr(obj, "to_dict") and callable(obj.to_dict):
        return obj.to_dict()
    if isinstance(obj, list):
        return [to_serializable(item) for item in obj]
    if isinstance(obj, dict):
        return {key: to_serializable(value) for key, value in obj.items()}
    return obj


def echo_json(obj: Any) -> None:
    """Print an object as pretty JSON."""
    typer.echo(json.dumps(to_serializable(obj), indent=2, default=str))
