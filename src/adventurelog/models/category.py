"""Category model."""

from __future__ import annotations

from adventurelog.models.common import AdventureLogModel


class Category(AdventureLogModel):
    """A location category (e.g. Restaurant, Hotel, Park)."""

    id: str | None = None
    name: str | None = None
    display_name: str | None = None
    icon: str | None = None
    num_locations: int | None = None
