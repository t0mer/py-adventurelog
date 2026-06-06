"""GenerateResource — wraps AI-generation, ICS calendar, and globe-spin endpoints."""

from __future__ import annotations

from typing import Any

from adventurelog.resources.base import BaseResource


class GenerateResource(BaseResource):
    """Resource for AI-generation and utility generation endpoints.

    Covers:
    - ``GET /api/generate/desc/``         — AI-generated location description
    - ``GET /api/generate/img/``          — AI-generated location image
    - ``GET /api/ics-calendar/generate/`` — ICS calendar export
    - ``GET /api/globespin/``             — Globe-spin data
    - ``GET /api/recommendations/query/`` — AI-powered recommendations
    """

    async def description(self, **params: Any) -> dict[str, Any]:
        """Generate an AI description for a location.

        Args:
            **params: Query parameters (e.g. ``location_id`` or ``name``).

        Returns:
            Raw response dict containing the generated description.
        """
        resp = await self._http.get("/api/generate/desc/", params=params or None)
        return dict(resp.json())

    async def image(self, **params: Any) -> dict[str, Any]:
        """Generate an AI image for a location.

        Args:
            **params: Query parameters (e.g. ``location_id`` or ``name``).

        Returns:
            Raw response dict containing the generated image URL or data.
        """
        resp = await self._http.get("/api/generate/img/", params=params or None)
        return dict(resp.json())

    async def ics_calendar(self, **params: Any) -> bytes:
        """Generate an ICS calendar export for the current user's adventures.

        Args:
            **params: Optional query parameters (e.g. date range filters).

        Returns:
            Raw ICS file bytes.
        """
        resp = await self._http.get(
            "/api/ics-calendar/generate/", params=params or None
        )
        return resp.content

    async def globespin(self, **params: Any) -> dict[str, Any]:
        """Retrieve globe-spin data (visited locations for 3-D globe rendering).

        Args:
            **params: Optional query parameters.

        Returns:
            Raw response dict.
        """
        resp = await self._http.get("/api/globespin/", params=params or None)
        return dict(resp.json())

    async def recommendations(self, **params: Any) -> dict[str, Any]:
        """Query AI-powered location recommendations.

        Args:
            **params: Query parameters (e.g. ``query``, ``limit``).

        Returns:
            Raw response dict with recommended locations.
        """
        resp = await self._http.get(
            "/api/recommendations/query/", params=params or None
        )
        return dict(resp.json())
