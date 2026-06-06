"""SearchResource — wraps /api/search/ and /api/tags/types/ endpoints."""

from __future__ import annotations

from typing import Any

from adventurelog.resources.base import BaseResource


class SearchResource(BaseResource):
    """Resource for global search and tag-type lookup endpoints.

    Covers:
    - ``GET /api/search/``      — full-text search across all content
    - ``GET /api/tags/types/``  — list of available tag type values
    """

    async def search(self, **params: Any) -> dict[str, Any]:
        """Perform a full-text search across all content types.

        Args:
            **params: Query parameters (e.g. ``query``, ``type``, ``page``).

        Returns:
            Raw response dict with search results.
        """
        resp = await self._http.get("/api/search/", params=params or None)
        return dict(resp.json())

    async def tag_types(self) -> list[dict[str, Any]]:
        """Return all available tag type values.

        Returns:
            List of raw tag-type dicts.
        """
        resp = await self._http.get("/api/tags/types/")
        return list(resp.json())
