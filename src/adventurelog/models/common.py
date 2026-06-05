"""Common/shared models and generic types."""

from __future__ import annotations

from typing import Generic, TypeVar

from pydantic import BaseModel, ConfigDict

T = TypeVar("T")


class AdventureLogModel(BaseModel):
    """Base model for all AdventureLog API models."""

    model_config = ConfigDict(extra="ignore", populate_by_name=True)


class PaginatedResponse(AdventureLogModel, Generic[T]):
    """Generic paginated response envelope returned by list endpoints."""

    count: int
    next: str | None = None
    previous: str | None = None
    results: list[T]
