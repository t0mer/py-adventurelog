"""Activity model."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from adventurelog.models.common import AdventureLogModel


class Activity(AdventureLogModel):
    """An activity (e.g. a hike, bike ride) linked to a visit."""

    id: str | None = None
    user: int | str | None = None
    visit: int | str | None = None
    trail: int | str | None = None
    gpx_file: str | None = None
    name: str | None = None
    sport_type: str | None = None
    distance: str | None = None  # DecimalField serialized as string
    moving_time: int | None = None
    elapsed_time: int | None = None
    rest_time: int | None = None
    elevation_gain: str | None = None  # DecimalField serialized as string
    elevation_loss: str | None = None  # DecimalField serialized as string
    elev_high: str | None = None  # DecimalField serialized as string
    elev_low: str | None = None  # DecimalField serialized as string
    start_date: datetime | None = None
    start_date_local: datetime | None = None
    timezone: str | None = None
    average_speed: str | None = None  # DecimalField serialized as string
    max_speed: str | None = None  # DecimalField serialized as string
    average_cadence: str | None = None  # DecimalField serialized as string
    calories: float | None = None
    start_lat: str | None = None  # DecimalField serialized as string
    start_lng: str | None = None  # DecimalField serialized as string
    end_lat: str | None = None  # DecimalField serialized as string
    end_lng: str | None = None  # DecimalField serialized as string
    external_service_id: str | None = None
    geojson: Any = None
