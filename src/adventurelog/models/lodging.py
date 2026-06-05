"""Lodging model."""

from __future__ import annotations

from datetime import datetime

from pydantic import ConfigDict

from adventurelog.models.attachment import Attachment
from adventurelog.models.common import AdventureLogModel
from adventurelog.models.image import ContentImage


class Lodging(AdventureLogModel):
    """A lodging (hotel, Airbnb, etc.) associated with a collection."""

    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    id: int | None = None
    user: int | str | None = None
    name: str | None = None
    description: str | None = None
    rating: str | None = None  # DecimalField serialized as string
    link: str | None = None
    check_in: datetime | None = None
    check_out: datetime | None = None
    reservation_number: str | None = None
    price: str | None = None  # DecimalField serialized as string
    price_currency: str | None = None
    latitude: str | None = None  # DecimalField serialized as string
    longitude: str | None = None  # DecimalField serialized as string
    location: str | None = None  # human-readable place name
    is_public: bool | None = None
    collection: int | str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
    type: str | None = None
    timezone: str | None = None
    images: list[ContentImage] = []
    attachments: list[Attachment] = []
