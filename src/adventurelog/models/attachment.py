"""Attachment model."""

from __future__ import annotations

from typing import Any

from pydantic import ConfigDict

from adventurelog.models.common import AdventureLogModel


class Attachment(AdventureLogModel):
    """A file attachment associated with a location or other content object."""

    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    id: int | None = None
    file: str | None = None  # URL
    extension: str | None = None
    name: str | None = None
    user: int | str | None = None
    geojson: Any = None
