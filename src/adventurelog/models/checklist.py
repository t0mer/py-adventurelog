"""Checklist and ChecklistItem models."""

from __future__ import annotations

from datetime import datetime

from pydantic import ConfigDict

from adventurelog.models.common import AdventureLogModel


class ChecklistItem(AdventureLogModel):
    """An individual item within a checklist."""

    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    id: int | None = None
    user: int | str | None = None
    name: str | None = None
    is_checked: bool | None = None
    checklist: int | str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None


class Checklist(AdventureLogModel):
    """A checklist associated with a collection."""

    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    id: int | None = None
    user: int | str | None = None
    name: str | None = None
    date: datetime | None = None
    is_public: bool | None = None
    collection: int | str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
    items: list[ChecklistItem] = []
