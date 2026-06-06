"""ReverseGeocodeResource — wraps /api/reverse-geocode/ endpoints."""

from __future__ import annotations

from typing import Any

from adventurelog.resources.base import BaseResource


class ReverseGeocodeResource(BaseResource):
    """Resource for reverse-geocoding and place-search endpoints.

    Covers:
    - ``GET  /api/reverse-geocode/reverse_geocode/``    — reverse-geocode a lat/lng
    - ``GET  /api/reverse-geocode/place_details/``      — detailed place info
    - ``GET  /api/reverse-geocode/search/``             — place name search
    - ``POST /api/reverse-geocode/mark_visited_region/``— mark a region visited
    """

    async def reverse_geocode(self, **params: Any) -> dict[str, Any]:
        """Reverse-geocode a latitude/longitude to a place.

        Args:
            **params: Query parameters — typically ``lat`` and ``lng``.

        Returns:
            Raw response dict with place name, region, country, etc.
        """
        resp = await self._http.get(
            "/api/reverse-geocode/reverse_geocode/", params=params or None
        )
        return dict(resp.json())

    async def place_details(self, **params: Any) -> dict[str, Any]:
        """Retrieve detailed information about a place.

        Args:
            **params: Query parameters (e.g. ``place_id``).

        Returns:
            Raw response dict with detailed place info.
        """
        resp = await self._http.get(
            "/api/reverse-geocode/place_details/", params=params or None
        )
        return dict(resp.json())

    async def search(self, **params: Any) -> dict[str, Any]:
        """Search for places by name or query string.

        Args:
            **params: Query parameters (e.g. ``query``, ``limit``).

        Returns:
            Raw response dict with matching places.
        """
        resp = await self._http.get(
            "/api/reverse-geocode/search/", params=params or None
        )
        return dict(resp.json())

    async def mark_visited_region(self, **params: Any) -> dict[str, Any]:
        """Mark the region containing a given lat/lng as visited.

        Args:
            **params: Body or query parameters (e.g. ``lat``, ``lng``).

        Returns:
            Raw response dict with the created or updated visited-region record.
        """
        resp = await self._http.post(
            "/api/reverse-geocode/mark_visited_region/",
            json=params if params else None,
        )
        return dict(resp.json())
