"""TransportationsResource — wraps /api/transportations/ endpoints."""

from __future__ import annotations

from typing import Any

from adventurelog.models.transportation import Transportation
from adventurelog.resources.base import BaseResource


class TransportationsResource(BaseResource):
    """Resource for the /api/transportations/ endpoint group.

    Transportations (flights, trains, car journeys, etc.) are associated with
    collections and returned as a plain JSON array (non-paginated).
    """

    async def list(self) -> list[Transportation]:
        """Return all transportation records for the current user.

        Returns:
            List of
            :class:`~adventurelog.models.transportation.Transportation` instances.
        """
        resp = await self._http.get("/api/transportations/")
        return [Transportation.model_validate(item) for item in resp.json()]

    async def get(self, id: str) -> Transportation:
        """Retrieve a single transportation record by ID.

        Args:
            id: The transportation's UUID.

        Returns:
            The matching :class:`~adventurelog.models.transportation.Transportation`.
        """
        resp = await self._http.get(f"/api/transportations/{id}/")
        return Transportation.model_validate(resp.json())

    async def create(self, data: dict[str, Any]) -> Transportation:
        """Create a new transportation record.

        Args:
            data: Transportation field data.

        Returns:
            The newly created
            :class:`~adventurelog.models.transportation.Transportation`.
        """
        resp = await self._http.post("/api/transportations/", json=data)
        return Transportation.model_validate(resp.json())

    async def update(self, id: str, data: dict[str, Any]) -> Transportation:
        """Replace a transportation record (full update).

        Args:
            id: The transportation's UUID.
            data: Complete transportation field data.

        Returns:
            The updated :class:`~adventurelog.models.transportation.Transportation`.
        """
        resp = await self._http.put(f"/api/transportations/{id}/", json=data)
        return Transportation.model_validate(resp.json())

    async def partial_update(self, id: str, data: dict[str, Any]) -> Transportation:
        """Partially update a transportation record.

        Args:
            id: The transportation's UUID.
            data: Fields to update.

        Returns:
            The updated :class:`~adventurelog.models.transportation.Transportation`.
        """
        resp = await self._http.patch(f"/api/transportations/{id}/", json=data)
        return Transportation.model_validate(resp.json())

    async def delete(self, id: str) -> None:
        """Delete a transportation record.

        Args:
            id: The transportation's UUID.
        """
        await self._http.delete(f"/api/transportations/{id}/")
