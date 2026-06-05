"""ContentImage model."""

from __future__ import annotations

from pydantic import ConfigDict

from adventurelog.models.common import AdventureLogModel


class ContentImage(AdventureLogModel):
    """An image associated with a content object (location, lodging, etc.)."""

    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    id: int | None = None
    image: str | None = None  # URL
    is_primary: bool | None = None
    user: int | None = None
    immich_id: str | None = None
