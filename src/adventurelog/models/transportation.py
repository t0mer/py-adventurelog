"""Transportation model."""

from __future__ import annotations

from datetime import datetime

from pydantic import ConfigDict

from adventurelog.models.attachment import Attachment
from adventurelog.models.common import AdventureLogModel
from adventurelog.models.image import ContentImage


class Transportation(AdventureLogModel):
    """A transportation leg (flight, train, etc.) associated with a collection."""

    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    id: int | None = None
    user: int | str | None = None
    type: str | None = None
    name: str | None = None
    description: str | None = None
    rating: str | None = None  # DecimalField serialized as string
    price: str | None = None  # DecimalField serialized as string
    price_currency: str | None = None
    link: str | None = None
    date: datetime | None = None
    flight_number: str | None = None
    from_location: str | None = None
    to_location: str | None = None
    is_public: bool | None = None
    collection: int | str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
    end_date: datetime | None = None
    origin_latitude: str | None = None  # DecimalField serialized as string
    origin_longitude: str | None = None  # DecimalField serialized as string
    destination_latitude: str | None = None  # DecimalField serialized as string
    destination_longitude: str | None = None  # DecimalField serialized as string
    start_timezone: str | None = None
    end_timezone: str | None = None
    distance: str | None = None  # DecimalField serialized as string
    images: list[ContentImage] = []
    attachments: list[Attachment] = []
    start_code: str | None = None
    end_code: str | None = None
    travel_duration_minutes: int | None = None
