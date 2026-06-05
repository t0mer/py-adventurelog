"""Category model."""

from __future__ import annotations

from pydantic import ConfigDict

from adventurelog.models.common import AdventureLogModel


class Category(AdventureLogModel):
    """A location category (e.g. Restaurant, Hotel, Park)."""

    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    id: int | None = None
    name: str | None = None
    display_name: str | None = None
    icon: str | None = None
    num_locations: int | None = None
