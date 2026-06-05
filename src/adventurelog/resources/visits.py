"""VisitsResource — wraps /api/visits/ endpoints."""

from __future__ import annotations

from typing import Any

from adventurelog.models.visit import Visit
from adventurelog.resources.base import BaseResource


class VisitsResource(BaseResource):
    """Resource for the /api/visits/ endpoint group.

    Visits record when a user went to a location, with optional date range
    and activities.  The list endpoint returns a plain JSON array
    (non-paginated).
    """

    async def list(self) -> list[Visit]:
        """Return all visits for the current user.

        Returns:
            List of :class:`~adventurelog.models.visit.Visit` instances.
        """
        resp = await self._http.get("/api/visits/")
        return [Visit.model_validate(item) for item in resp.json()]

    async def get(self, id: str) -> Visit:
        """Retrieve a single visit by ID.

        Args:
            id: The visit's UUID.

        Returns:
            The matching :class:`~adventurelog.models.visit.Visit`.
        """
        resp = await self._http.get(f"/api/visits/{id}/")
        return Visit.model_validate(resp.json())

    async def create(self, data: dict[str, Any]) -> Visit:
        """Create a new visit.

        Args:
            data: Visit field data.

        Returns:
            The newly created :class:`~adventurelog.models.visit.Visit`.
        """
        resp = await self._http.post("/api/visits/", json=data)
        return Visit.model_validate(resp.json())

    async def update(self, id: str, data: dict[str, Any]) -> Visit:
        """Replace a visit (full update).

        Args:
            id: The visit's UUID.
            data: Complete visit field data.

        Returns:
            The updated :class:`~adventurelog.models.visit.Visit`.
        """
        resp = await self._http.put(f"/api/visits/{id}/", json=data)
        return Visit.model_validate(resp.json())

    async def partial_update(self, id: str, data: dict[str, Any]) -> Visit:
        """Partially update a visit.

        Args:
            id: The visit's UUID.
            data: Fields to update.

        Returns:
            The updated :class:`~adventurelog.models.visit.Visit`.
        """
        resp = await self._http.patch(f"/api/visits/{id}/", json=data)
        return Visit.model_validate(resp.json())

    async def delete(self, id: str) -> None:
        """Delete a visit.

        Args:
            id: The visit's UUID.
        """
        await self._http.delete(f"/api/visits/{id}/")
