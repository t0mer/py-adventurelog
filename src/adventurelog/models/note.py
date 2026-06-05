"""Note model."""

from __future__ import annotations

from datetime import datetime

from pydantic import ConfigDict

from adventurelog.models.common import AdventureLogModel


class Note(AdventureLogModel):
    """A note associated with a collection."""

    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    id: int | None = None
    user: int | str | None = None
    name: str | None = None
    content: str | None = None
    date: datetime | None = None
    links: list[str] = []
    is_public: bool | None = None
    collection: int | str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
