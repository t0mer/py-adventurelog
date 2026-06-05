"""Location model (the core entity in AdventureLog)."""

from __future__ import annotations

from datetime import datetime

from adventurelog.models.attachment import Attachment
from adventurelog.models.category import Category
from adventurelog.models.common import AdventureLogModel
from adventurelog.models.geo import City, Country, Region
from adventurelog.models.image import ContentImage
from adventurelog.models.trail import Trail
from adventurelog.models.visit import Visit


class Location(AdventureLogModel):
    """A location (place visited or planned) — the core AdventureLog entity."""

    id: str | None = None
    name: str | None = None
    description: str | None = None
    rating: str | None = None  # DecimalField serialized as string
    tags: list[str] = []
    location: str | None = None  # human-readable place name
    is_public: bool | None = None
    collections: list[int | str] = []  # array of UltraSlimCollection or FK ids
    created_at: datetime | None = None
    updated_at: datetime | None = None
    images: list[ContentImage] = []
    link: str | None = None
    longitude: str | None = None  # DecimalField serialized as string
    latitude: str | None = None  # DecimalField serialized as string
    visits: list[Visit] = []
    is_visited: str | bool | None = None  # spec says string but behaves as boolean
    category: Category | None = None
    attachments: list[Attachment] = []
    user: int | str | None = None
    city: City | None = None
    country: Country | None = None
    region: Region | None = None
    trails: list[Trail] = []
    price: str | None = None  # DecimalField serialized as string
    price_currency: str | None = None
