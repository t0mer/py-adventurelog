"""Collection, UltraSlimCollection, and itinerary models."""

from __future__ import annotations

import datetime
from datetime import date
from datetime import datetime as DateTime
from typing import Any

from adventurelog.models.common import AdventureLogModel
from adventurelog.models.image import ContentImage


class UltraSlimCollection(AdventureLogModel):
    """Slim collection reference embedded in location responses."""

    id: str | None = None
    user: int | str | None = None
    name: str | None = None
    description: str | None = None
    is_public: bool | None = None
    start_date: date | None = None
    end_date: date | None = None
    is_archived: bool | None = None
    link: str | None = None
    created_at: DateTime | None = None
    updated_at: DateTime | None = None
    location_images: str | None = None  # HyperlinkedRelatedField — URL string
    location_count: int | None = None
    shared_with: list[Any] = []
    collaborators: list[Any] = []
    status: str | None = None
    days_until_start: int | None = None
    primary_image: ContentImage | None = None


class Collection(AdventureLogModel):
    """A collection (trip/itinerary) grouping locations and other content."""

    id: str | None = None
    description: str | None = None
    user: int | str | None = None
    name: str | None = None
    is_public: bool | None = None
    # DRF HyperlinkedRelatedField — returns URL strings in nested list views
    locations: str | None = None
    created_at: DateTime | None = None
    start_date: date | None = None
    end_date: date | None = None
    transportations: str | None = None
    notes: str | None = None
    updated_at: DateTime | None = None
    checklists: str | None = None
    is_archived: bool | None = None
    shared_with: list[Any] = []
    collaborators: str | None = None
    link: str | None = None
    lodging: str | None = None
    status: str | None = None
    days_until_start: int | None = None
    primary_image: ContentImage | None = None
    primary_image_id: str | None = None


class CollectionItineraryDay(AdventureLogModel):
    """A day within a collection itinerary."""

    id: str | None = None
    collection: int | str | None = None
    date: datetime.date | None = None
    name: str | None = None
    description: str | None = None
    created_at: DateTime | None = None
    updated_at: DateTime | None = None


class CollectionItineraryItem(AdventureLogModel):
    """An item (location, transportation, etc.) within a collection itinerary day."""

    id: str | None = None
    collection: int | str | None = None
    content_type: int | None = None
    object_id: int | str | None = None
    item: Any = None  # generic content-type resolved object
    date: datetime.date | None = None
    is_global: bool | None = None
    order: int | None = None
    start_datetime: DateTime | None = None
    end_datetime: DateTime | None = None
    created_at: DateTime | None = None
    object_name: str | None = None
