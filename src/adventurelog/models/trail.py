"""Trail model."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from adventurelog.models.common import AdventureLogModel


class Trail(AdventureLogModel):
    """A trail associated with a location."""

    id: str | None = None
    user: int | str | None = None
    name: str | None = None
    location: str | None = None
    created_at: datetime | None = None
    link: str | None = None
    wanderer_id: str | None = None
    provider: str | None = None
    wanderer_data: Any = None
    wanderer_link: str | None = None
