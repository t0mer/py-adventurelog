"""StatsResource — wraps /api/stats/ endpoints."""

from __future__ import annotations

from typing import Any

from adventurelog.resources.base import BaseResource


class StatsResource(BaseResource):
    """Resource for statistics endpoints.

    Covers:
    - ``GET /api/stats/counts/{username}/`` — adventure count stats for a user
    """

    async def counts(self, username: str) -> dict[str, Any]:
        """Return adventure count statistics for a given user.

        Args:
            username: The target user's username.

        Returns:
            Raw response dict with count breakdowns (locations visited,
            countries, collections, etc.).
        """
        resp = await self._http.get(f"/api/stats/counts/{username}/")
        return dict(resp.json())
