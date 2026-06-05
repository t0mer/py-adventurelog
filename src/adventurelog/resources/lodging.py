"""LodgingResource — wraps /api/lodging/ endpoints."""

from __future__ import annotations

from typing import Any

from adventurelog.models.lodging import Lodging
from adventurelog.resources.base import BaseResource


class LodgingResource(BaseResource):
    """Resource for the /api/lodging/ endpoint group.

    Lodging records (hotels, Airbnbs, etc.) are associated with collections
    and returned as a plain JSON array (non-paginated).
    """

    async def list(self) -> list[Lodging]:
        """Return all lodging records for the current user.

        Returns:
            List of :class:`~adventurelog.models.lodging.Lodging` instances.
        """
        resp = await self._http.get("/api/lodging/")
        return [Lodging.model_validate(item) for item in resp.json()]

    async def get(self, id: str) -> Lodging:
        """Retrieve a single lodging record by ID.

        Args:
            id: The lodging's UUID.

        Returns:
            The matching :class:`~adventurelog.models.lodging.Lodging`.
        """
        resp = await self._http.get(f"/api/lodging/{id}/")
        return Lodging.model_validate(resp.json())

    async def create(self, data: dict[str, Any]) -> Lodging:
        """Create a new lodging record.

        Args:
            data: Lodging field data.

        Returns:
            The newly created :class:`~adventurelog.models.lodging.Lodging`.
        """
        resp = await self._http.post("/api/lodging/", json=data)
        return Lodging.model_validate(resp.json())

    async def update(self, id: str, data: dict[str, Any]) -> Lodging:
        """Replace a lodging record (full update).

        Args:
            id: The lodging's UUID.
            data: Complete lodging field data.

        Returns:
            The updated :class:`~adventurelog.models.lodging.Lodging`.
        """
        resp = await self._http.put(f"/api/lodging/{id}/", json=data)
        return Lodging.model_validate(resp.json())

    async def partial_update(self, id: str, data: dict[str, Any]) -> Lodging:
        """Partially update a lodging record.

        Args:
            id: The lodging's UUID.
            data: Fields to update.

        Returns:
            The updated :class:`~adventurelog.models.lodging.Lodging`.
        """
        resp = await self._http.patch(f"/api/lodging/{id}/", json=data)
        return Lodging.model_validate(resp.json())

    async def delete(self, id: str) -> None:
        """Delete a lodging record.

        Args:
            id: The lodging's UUID.
        """
        await self._http.delete(f"/api/lodging/{id}/")
