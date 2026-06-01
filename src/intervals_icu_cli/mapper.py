from __future__ import annotations

from intervals_icu_client import EventEx

from intervals_icu_cli.models import EventCreateRequest


def map_event_create_request_to_intervals_api(event: EventCreateRequest) -> EventEx:
    start_dt = event.date
    start_iso = start_dt.replace(microsecond=0).strftime("%Y-%m-%dT%H:%M:%S")

    description = (event.description or "") + "\n" + event.workout.to_text()

    event_ex = EventEx(
        name=event.name,
        start_date_local=start_iso,
        description=description,
        category=event.category,
        type=event.type,
    )
    return event_ex
