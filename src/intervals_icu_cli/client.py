from __future__ import annotations

import os
from dataclasses import dataclass
from datetime import date

from intervals_icu_client.api.activities_api import ActivitiesApi
from intervals_icu_client.api.events_api import EventsApi
from intervals_icu_client.api_client import ApiClient
from intervals_icu_client.configuration import Configuration
from intervals_icu_client.models import EventEx
from intervals_icu_client.models.activity import Activity
from intervals_icu_client.models.event import Event

from intervals_icu_cli.config import DEFAULT_BASE_URL, read_config_file


class IntervalsAuthError(RuntimeError):
    """Raised when Intervals.icu credentials are missing or invalid."""


@dataclass
class IntervalsConfig:
    base_url: str
    athlete_id: str
    api_key: str

    @classmethod
    def resolve(cls) -> IntervalsConfig:
        """Resolve credentials, preferring environment variables over the config file."""
        file_data = read_config_file()

        athlete_id = os.getenv("INTERVALS_ICU_ATHLETE_ID") or file_data.get(
            "athlete_id"
        )
        api_key = os.getenv("INTERVALS_ICU_API_KEY") or file_data.get("api_key")
        base_url = (
            os.getenv("INTERVALS_ICU_BASE_URL")
            or file_data.get("base_url")
            or DEFAULT_BASE_URL
        )

        if not athlete_id or not api_key:
            raise IntervalsAuthError(
                "Missing credentials. Set INTERVALS_ICU_ATHLETE_ID and "
                "INTERVALS_ICU_API_KEY, or run 'intervals-icu auth login'."
            )

        return cls(
            base_url=base_url.rstrip("/"), athlete_id=athlete_id, api_key=api_key
        )

    @classmethod
    def from_env(cls) -> IntervalsConfig:
        """Backwards-compatible alias for resolve()."""
        return cls.resolve()


class IntervalsClient:
    """Thin wrapper around the generated `intervals_icu_client` package."""

    def __init__(
        self,
        config: IntervalsConfig | None = None,
        api_client: ApiClient | None = None,
    ) -> None:
        self._config = config or IntervalsConfig.resolve()
        if api_client is None:
            configuration = Configuration(
                host=self._config.base_url.rstrip("/"),
                username="API_KEY",
                password=self._config.api_key,
            )
            api_client = ApiClient(configuration=configuration)

        self._api_client = api_client
        self._activities_api = ActivitiesApi(self._api_client)
        self._events_api = EventsApi(self._api_client)

    def close(self) -> None:
        """Close the underlying API client session."""
        close = getattr(self._api_client, "close", None)
        if callable(close):
            close()

    def list_activities(
        self,
        *,
        start: date,
        end: date,
        limit: int | None = None,
    ) -> list[Activity]:
        """List activities for the configured athlete between two dates."""
        return self._activities_api.list_activities(
            id=self._config.athlete_id,
            oldest=start.isoformat(),
            newest=end.isoformat(),
            limit=limit,
        )

    def list_events(
        self,
        *,
        oldest: date,
        newest: date,
        category: str | None = None,
        limit: int | None = None,
    ) -> list[Event]:
        """List calendar events for the configured athlete."""
        return self._events_api.list_events(
            id=self._config.athlete_id,
            oldest=oldest.isoformat(),
            newest=newest.isoformat(),
            category=[category] if category is not None else None,
            limit=limit,
            format="json",
        )

    def create_event(self, event_ex: EventEx) -> Event:
        """Create a new event on the athlete's calendar."""
        return self._events_api.create_event(
            id=self._config.athlete_id,
            upsert_on_uid=True,
            event_ex=event_ex,
        )

    def update_event(self, event_id: int, event_ex: EventEx) -> Event:
        """Update an existing event on the athlete's calendar."""
        return self._events_api.update_event(
            id=self._config.athlete_id,
            event_id=event_id,
            event_ex=event_ex,
        )

    def delete_event(self, event_id: int) -> dict[str, object]:
        return self._events_api.delete_event(
            id=self._config.athlete_id, event_id=event_id
        )


def get_intervals_client() -> IntervalsClient:
    """Factory that builds an IntervalsClient from environment configuration."""
    return IntervalsClient()
