"""Attachment model."""

from __future__ import annotations

from typing import Any

from adventurelog.models.common import AdventureLogModel


class Attachment(AdventureLogModel):
    """A file attachment associated with a location or other content object."""

    id: str | None = None
    file: str | None = None  # URL
    extension: str | None = None
    name: str | None = None
    user: int | str | None = None
    geojson: Any = None
