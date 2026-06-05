"""Collection, UltraSlimCollection, and itinerary models."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import ConfigDict

from adventurelog.models.common import AdventureLogModel
from adventurelog.models.image import ContentImage


class UltraSlimCollection(AdventureLogModel):
    """Slim collection reference embedded in location responses."""

    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    id: int | None = None
    user: int | str | None = None
    name: str | None = None
    description: str | None = None
    is_public: bool | None = None
    start_date: datetime | None = None
    end_date: datetime | None = None
    is_archived: bool | None = None
    link: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
    location_images: list[ContentImage] = []
    location_count: int | None = None
    shared_with: list[Any] = []
    collaborators: list[Any] = []
    status: str | None = None
    days_until_start: int | None = None
    primary_image: ContentImage | None = None


class Collection(AdventureLogModel):
    """A collection (trip/itinerary) grouping locations and other content."""

    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    id: int | None = None
    description: str | None = None
    user: int | str | None = None
    name: str | None = None
    is_public: bool | None = None
    # DRF HyperlinkedRelatedField — returns URL strings in nested list views
    locations: str | None = None
    created_at: datetime | None = None
    start_date: datetime | None = None
    end_date: datetime | None = None
    transportations: str | None = None
    notes: str | None = None
    updated_at: datetime | None = None
    checklists: str | None = None
    is_archived: bool | None = None
    shared_with: list[Any] = []
    collaborators: str | None = None
    link: str | None = None
    lodging: str | None = None
    status: str | None = None
    days_until_start: int | None = None
    primary_image: ContentImage | None = None
    primary_image_id: int | None = None


class CollectionItineraryDay(AdventureLogModel):
    """A day within a collection itinerary."""

    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    id: int | None = None
    collection: int | str | None = None
    date: datetime | None = None
    name: str | None = None
    description: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None


class CollectionItineraryItem(AdventureLogModel):
    """An item (location, transportation, etc.) within a collection itinerary day."""

    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    id: int | None = None
    collection: int | str | None = None
    content_type: str | None = None
    object_id: int | str | None = None
    item: Any = None  # generic content-type resolved object
    date: datetime | None = None
    is_global: bool | None = None
    order: int | None = None
    start_datetime: datetime | None = None
    end_datetime: datetime | None = None
    created_at: datetime | None = None
    object_name: str | None = None
