"""Checklist and ChecklistItem models."""

from __future__ import annotations

import datetime
from datetime import datetime as DateTime

from adventurelog.models.common import AdventureLogModel


class ChecklistItem(AdventureLogModel):
    """An individual item within a checklist."""

    id: str | None = None
    user: int | str | None = None
    name: str | None = None
    is_checked: bool | None = None
    checklist: int | str | None = None
    created_at: DateTime | None = None
    updated_at: DateTime | None = None


class Checklist(AdventureLogModel):
    """A checklist associated with a collection."""

    id: str | None = None
    user: int | str | None = None
    name: str | None = None
    date: datetime.date | None = None
    is_public: bool | None = None
    collection: int | str | None = None
    created_at: DateTime | None = None
    updated_at: DateTime | None = None
    items: list[ChecklistItem] = []
