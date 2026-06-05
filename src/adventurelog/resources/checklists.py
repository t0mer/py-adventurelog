"""ChecklistsResource — wraps /api/checklists/ endpoints."""

from __future__ import annotations

from typing import Any

from adventurelog.models.checklist import Checklist
from adventurelog.resources.base import BaseResource


class ChecklistsResource(BaseResource):
    """Resource for the /api/checklists/ endpoint group.

    Checklists are task lists associated with collections and returned as a
    plain JSON array (non-paginated).
    """

    async def list(self) -> list[Checklist]:
        """Return all checklists for the current user.

        Returns:
            List of :class:`~adventurelog.models.checklist.Checklist` instances.
        """
        resp = await self._http.get("/api/checklists/")
        return [Checklist.model_validate(item) for item in resp.json()]

    async def get(self, id: str) -> Checklist:
        """Retrieve a single checklist by ID.

        Args:
            id: The checklist's UUID.

        Returns:
            The matching :class:`~adventurelog.models.checklist.Checklist`.
        """
        resp = await self._http.get(f"/api/checklists/{id}/")
        return Checklist.model_validate(resp.json())

    async def create(self, data: dict[str, Any]) -> Checklist:
        """Create a new checklist.

        Args:
            data: Checklist field data.

        Returns:
            The newly created :class:`~adventurelog.models.checklist.Checklist`.
        """
        resp = await self._http.post("/api/checklists/", json=data)
        return Checklist.model_validate(resp.json())

    async def update(self, id: str, data: dict[str, Any]) -> Checklist:
        """Replace a checklist (full update).

        Args:
            id: The checklist's UUID.
            data: Complete checklist field data.

        Returns:
            The updated :class:`~adventurelog.models.checklist.Checklist`.
        """
        resp = await self._http.put(f"/api/checklists/{id}/", json=data)
        return Checklist.model_validate(resp.json())

    async def partial_update(self, id: str, data: dict[str, Any]) -> Checklist:
        """Partially update a checklist.

        Args:
            id: The checklist's UUID.
            data: Fields to update.

        Returns:
            The updated :class:`~adventurelog.models.checklist.Checklist`.
        """
        resp = await self._http.patch(f"/api/checklists/{id}/", json=data)
        return Checklist.model_validate(resp.json())

    async def delete(self, id: str) -> None:
        """Delete a checklist.

        Args:
            id: The checklist's UUID.
        """
        await self._http.delete(f"/api/checklists/{id}/")
