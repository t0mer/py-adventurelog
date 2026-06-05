"""TrailsResource — wraps /api/trails/ endpoints."""

from __future__ import annotations

from typing import Any

from adventurelog.models.trail import Trail
from adventurelog.resources.base import BaseResource


class TrailsResource(BaseResource):
    """Resource for the /api/trails/ endpoint group.

    Trails are associated with locations and returned as a plain JSON array
    (non-paginated).
    """

    async def list(self) -> list[Trail]:
        """Return all trails for the current user.

        Returns:
            List of :class:`~adventurelog.models.trail.Trail` instances.
        """
        resp = await self._http.get("/api/trails/")
        return [Trail.model_validate(item) for item in resp.json()]

    async def get(self, id: str) -> Trail:
        """Retrieve a single trail by ID.

        Args:
            id: The trail's UUID.

        Returns:
            The matching :class:`~adventurelog.models.trail.Trail`.
        """
        resp = await self._http.get(f"/api/trails/{id}/")
        return Trail.model_validate(resp.json())

    async def create(self, data: dict[str, Any]) -> Trail:
        """Create a new trail.

        Args:
            data: Trail field data.

        Returns:
            The newly created :class:`~adventurelog.models.trail.Trail`.
        """
        resp = await self._http.post("/api/trails/", json=data)
        return Trail.model_validate(resp.json())

    async def update(self, id: str, data: dict[str, Any]) -> Trail:
        """Replace a trail (full update).

        Args:
            id: The trail's UUID.
            data: Complete trail field data.

        Returns:
            The updated :class:`~adventurelog.models.trail.Trail`.
        """
        resp = await self._http.put(f"/api/trails/{id}/", json=data)
        return Trail.model_validate(resp.json())

    async def partial_update(self, id: str, data: dict[str, Any]) -> Trail:
        """Partially update a trail.

        Args:
            id: The trail's UUID.
            data: Fields to update.

        Returns:
            The updated :class:`~adventurelog.models.trail.Trail`.
        """
        resp = await self._http.patch(f"/api/trails/{id}/", json=data)
        return Trail.model_validate(resp.json())

    async def delete(self, id: str) -> None:
        """Delete a trail.

        Args:
            id: The trail's UUID.
        """
        await self._http.delete(f"/api/trails/{id}/")
