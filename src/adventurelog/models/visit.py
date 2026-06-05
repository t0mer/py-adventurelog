"""Visit model."""

from __future__ import annotations

from datetime import datetime

from pydantic import ConfigDict

from adventurelog.models.activity import Activity
from adventurelog.models.common import AdventureLogModel


class Visit(AdventureLogModel):
    """A visit to a location, with optional date range and activities."""

    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    id: int | None = None
    start_date: datetime | None = None
    end_date: datetime | None = None
    timezone: str | None = None
    notes: str | None = None
    activities: list[Activity] = []
    # FK to Location — kept as int/str to avoid circular import with location.py
    location: int | str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
