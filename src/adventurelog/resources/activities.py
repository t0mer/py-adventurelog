"""ActivitiesResource — wraps /api/activities/ endpoints."""

from __future__ import annotations

from typing import Any

from adventurelog.models.activity import Activity
from adventurelog.resources.base import BaseResource


class ActivitiesResource(BaseResource):
    """Resource for the /api/activities/ endpoint group.

    Activities (e.g. hikes, bike rides) are linked to visits of locations.
    This endpoint returns a plain JSON array (non-paginated).
    """

    async def list(self) -> list[Activity]:
        """Return all activities for the current user.

        Returns:
            List of :class:`~adventurelog.models.activity.Activity` instances.
        """
        resp = await self._http.get("/api/activities/")
        return [Activity.model_validate(item) for item in resp.json()]

    async def get(self, id: str) -> Activity:
        """Retrieve a single activity by ID.

        Args:
            id: The activity's UUID.

        Returns:
            The matching :class:`~adventurelog.models.activity.Activity`.
        """
        resp = await self._http.get(f"/api/activities/{id}/")
        return Activity.model_validate(resp.json())

    async def create(self, data: dict[str, Any]) -> Activity:
        """Create a new activity.

        Args:
            data: Activity field data.

        Returns:
            The newly created :class:`~adventurelog.models.activity.Activity`.
        """
        resp = await self._http.post("/api/activities/", json=data)
        return Activity.model_validate(resp.json())

    async def update(self, id: str, data: dict[str, Any]) -> Activity:
        """Replace an activity (full update).

        Args:
            id: The activity's UUID.
            data: Complete activity field data.

        Returns:
            The updated :class:`~adventurelog.models.activity.Activity`.
        """
        resp = await self._http.put(f"/api/activities/{id}/", json=data)
        return Activity.model_validate(resp.json())

    async def partial_update(self, id: str, data: dict[str, Any]) -> Activity:
        """Partially update an activity.

        Args:
            id: The activity's UUID.
            data: Fields to update.

        Returns:
            The updated :class:`~adventurelog.models.activity.Activity`.
        """
        resp = await self._http.patch(f"/api/activities/{id}/", json=data)
        return Activity.model_validate(resp.json())

    async def delete(self, id: str) -> None:
        """Delete an activity.

        Args:
            id: The activity's UUID.
        """
        await self._http.delete(f"/api/activities/{id}/")
