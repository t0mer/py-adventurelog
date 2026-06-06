"""LocationsResource — wraps /api/locations/ endpoints."""

from __future__ import annotations

from collections.abc import AsyncIterator
from typing import Any

from adventurelog.models.common import PaginatedResponse
from adventurelog.models.location import Location
from adventurelog.pagination import fetch_page, paginate
from adventurelog.resources.base import BaseResource


class LocationsResource(BaseResource):
    """Resource for the /api/locations/ endpoint group.

    Locations are the core entity in AdventureLog — a place visited or
    planned.  This resource covers paginated listing, single-item CRUD, and
    a handful of action endpoints.
    """

    async def list(
        self, *, page_size: int = 20, **params: Any
    ) -> AsyncIterator[Location]:
        """Async generator over all locations (follows pagination automatically).

        Args:
            page_size: Number of items per page request.
            **params: Additional query parameters forwarded to the server
                (e.g. ``is_visited=True``, ``collection=<id>``).

        Yields:
            :class:`~adventurelog.models.location.Location` instances.
        """
        async for item in paginate(
            self._http,
            "/api/locations/",
            params={"page_size": page_size, **params},
        ):
            yield Location.model_validate(item)

    async def page(
        self,
        *,
        page: int = 1,
        page_size: int = 20,
        **params: Any,
    ) -> PaginatedResponse[Location]:
        """Fetch a single page of locations.

        Args:
            page: Page number (1-based).
            page_size: Number of items per page.
            **params: Additional query parameters.

        Returns:
            :class:`~adventurelog.models.common.PaginatedResponse` containing
            the page results and pagination metadata.
        """
        raw = await fetch_page(
            self._http,
            "/api/locations/",
            page=page,
            page_size=page_size,
            params=params or None,
        )
        results = [Location.model_validate(r) for r in raw.get("results", [])]
        return PaginatedResponse[Location].model_validate({**raw, "results": results})

    async def get(self, id: str) -> Location:
        """Retrieve a single location by ID.

        Args:
            id: The location's UUID.

        Returns:
            The matching :class:`~adventurelog.models.location.Location`.
        """
        resp = await self._http.get(f"/api/locations/{id}/")
        return Location.model_validate(resp.json())

    async def create(self, data: dict[str, Any]) -> Location:
        """Create a new location.

        Args:
            data: Location field data as a dict.

        Returns:
            The newly created :class:`~adventurelog.models.location.Location`.
        """
        resp = await self._http.post("/api/locations/", json=data)
        return Location.model_validate(resp.json())

    async def update(self, id: str, data: dict[str, Any]) -> Location:
        """Replace a location (full update).

        Args:
            id: The location's UUID.
            data: Complete location field data.

        Returns:
            The updated :class:`~adventurelog.models.location.Location`.
        """
        resp = await self._http.put(f"/api/locations/{id}/", json=data)
        return Location.model_validate(resp.json())

    async def partial_update(self, id: str, data: dict[str, Any]) -> Location:
        """Partially update a location.

        Args:
            id: The location's UUID.
            data: Fields to update.

        Returns:
            The updated :class:`~adventurelog.models.location.Location`.
        """
        resp = await self._http.patch(f"/api/locations/{id}/", json=data)
        return Location.model_validate(resp.json())

    async def delete(self, id: str) -> None:
        """Delete a location.

        Args:
            id: The location's UUID.
        """
        await self._http.delete(f"/api/locations/{id}/")

    async def all_locations(
        self, *, page_size: int = 100, **params: Any
    ) -> AsyncIterator[Location]:
        """Async generator over all locations via the /all/ endpoint.

        This endpoint typically returns all locations without applying the
        default visibility filters.

        Args:
            page_size: Items per page.
            **params: Additional query parameters.

        Yields:
            :class:`~adventurelog.models.location.Location` instances.
        """
        async for item in paginate(
            self._http,
            "/api/locations/all/",
            params={"page_size": page_size, **params},
        ):
            yield Location.model_validate(item)

    async def quick_add(self, data: dict[str, Any]) -> Location:
        """Create a location via the quick-add shortcut endpoint.

        Args:
            data: Minimal location data for quick creation.

        Returns:
            The newly created :class:`~adventurelog.models.location.Location`.
        """
        resp = await self._http.post("/api/locations/quick-add/", json=data)
        return Location.model_validate(resp.json())

    async def duplicate(self, id: str) -> Location:
        """Duplicate an existing location.

        Args:
            id: The UUID of the location to duplicate.

        Returns:
            The newly created duplicate :class:`~adventurelog.models.location.Location`.
        """
        resp = await self._http.post(f"/api/locations/{id}/duplicate/")
        return Location.model_validate(resp.json())

    async def calendar(
        self, *, page_size: int = 20, **params: Any
    ) -> AsyncIterator[Location]:
        """Async generator over locations in calendar view.

        Args:
            page_size: Items per page.
            **params: Additional query parameters (e.g. date range filters).

        Yields:
            :class:`~adventurelog.models.location.Location` instances.
        """
        async for item in paginate(
            self._http,
            "/api/locations/calendar/",
            params={"page_size": page_size, **params},
        ):
            yield Location.model_validate(item)

    async def filtered(
        self, *, page_size: int = 20, **params: Any
    ) -> AsyncIterator[Location]:
        """Async generator over filtered locations.

        Args:
            page_size: Items per page.
            **params: Filter parameters forwarded to the server.

        Yields:
            :class:`~adventurelog.models.location.Location` instances.
        """
        async for item in paginate(
            self._http,
            "/api/locations/filtered/",
            params={"page_size": page_size, **params},
        ):
            yield Location.model_validate(item)

    async def pins(
        self, *, page_size: int = 20, **params: Any
    ) -> AsyncIterator[Location]:
        """Async generator over map-pin locations.

        Args:
            page_size: Items per page.
            **params: Additional query parameters.

        Yields:
            :class:`~adventurelog.models.location.Location` instances.
        """
        async for item in paginate(
            self._http,
            "/api/locations/pins/",
            params={"page_size": page_size, **params},
        ):
            yield Location.model_validate(item)

    async def additional_info(self, id: str) -> dict[str, Any]:
        """Retrieve additional metadata for a location.

        Args:
            id: The location's UUID.

        Returns:
            Raw response dict with extra location info.
        """
        resp = await self._http.get(f"/api/locations/{id}/additional-info/")
        return dict(resp.json())
