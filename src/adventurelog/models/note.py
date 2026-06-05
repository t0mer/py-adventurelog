"""Note model."""

from __future__ import annotations

import datetime
from datetime import datetime as DateTime

from adventurelog.models.common import AdventureLogModel


class Note(AdventureLogModel):
    """A note associated with a collection."""

    id: str | None = None
    user: int | str | None = None
    name: str | None = None
    content: str | None = None
    date: datetime.date | None = None
    links: list[str] = []
    is_public: bool | None = None
    collection: int | str | None = None
    created_at: DateTime | None = None
    updated_at: DateTime | None = None
