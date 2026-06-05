"""CollectionsResource — wraps /api/collections/ endpoints."""

from __future__ import annotations

from collections.abc import AsyncIterator
from typing import Any

from adventurelog.models.collection import Collection
from adventurelog.models.common import PaginatedResponse
from adventurelog.pagination import fetch_page, paginate
from adventurelog.resources.base import BaseResource


class CollectionsResource(BaseResource):
    """Resource for the /api/collections/ endpoint group.

    Collections (trips/itineraries) group locations and other travel content.
    """

    async def list(
        self, *, page_size: int = 20, **params: Any
    ) -> AsyncIterator[Collection]:
        """Async generator over all collections.

        Args:
            page_size: Items per page.
            **params: Additional query parameters.

        Yields:
            :class:`~adventurelog.models.collection.Collection` instances.
        """
        async for item in paginate(
            self._http,
            "/api/collections/",
            params={"page_size": page_size, **params},
        ):
            yield Collection.model_validate(item)

    async def page(
        self,
        *,
        page: int = 1,
        page_size: int = 20,
        **params: Any,
    ) -> PaginatedResponse[Collection]:
        """Fetch a single page of collections.

        Args:
            page: Page number (1-based).
            page_size: Items per page.
            **params: Additional query parameters.

        Returns:
            :class:`~adventurelog.models.common.PaginatedResponse` of collections.
        """
        raw = await fetch_page(
            self._http,
            "/api/collections/",
            page=page,
            page_size=page_size,
            params=params or None,
        )
        results = [Collection.model_validate(r) for r in raw.get("results", [])]
        return PaginatedResponse[Collection].model_validate({**raw, "results": results})

    async def get(self, id: str) -> Collection:
        """Retrieve a single collection by ID.

        Args:
            id: The collection's UUID.

        Returns:
            The matching :class:`~adventurelog.models.collection.Collection`.
        """
        resp = await self._http.get(f"/api/collections/{id}/")
        return Collection.model_validate(resp.json())

    async def create(self, data: dict[str, Any]) -> Collection:
        """Create a new collection.

        Args:
            data: Collection field data.

        Returns:
            The newly created :class:`~adventurelog.models.collection.Collection`.
        """
        resp = await self._http.post("/api/collections/", json=data)
        return Collection.model_validate(resp.json())

    async def update(self, id: str, data: dict[str, Any]) -> Collection:
        """Replace a collection (full update).

        Args:
            id: The collection's UUID.
            data: Complete collection field data.

        Returns:
            The updated :class:`~adventurelog.models.collection.Collection`.
        """
        resp = await self._http.put(f"/api/collections/{id}/", json=data)
        return Collection.model_validate(resp.json())

    async def partial_update(self, id: str, data: dict[str, Any]) -> Collection:
        """Partially update a collection.

        Args:
            id: The collection's UUID.
            data: Fields to update.

        Returns:
            The updated :class:`~adventurelog.models.collection.Collection`.
        """
        resp = await self._http.patch(f"/api/collections/{id}/", json=data)
        return Collection.model_validate(resp.json())

    async def delete(self, id: str) -> None:
        """Delete a collection.

        Args:
            id: The collection's UUID.
        """
        await self._http.delete(f"/api/collections/{id}/")

    async def archived(
        self, *, page_size: int = 20, **params: Any
    ) -> AsyncIterator[Collection]:
        """Async generator over archived collections.

        Args:
            page_size: Items per page.
            **params: Additional query parameters.

        Yields:
            Archived :class:`~adventurelog.models.collection.Collection` instances.
        """
        async for item in paginate(
            self._http,
            "/api/collections/archived/",
            params={"page_size": page_size, **params},
        ):
            yield Collection.model_validate(item)

    async def shared(
        self, *, page_size: int = 20, **params: Any
    ) -> AsyncIterator[Collection]:
        """Async generator over collections shared with the current user.

        Args:
            page_size: Items per page.
            **params: Additional query parameters.

        Yields:
            Shared :class:`~adventurelog.models.collection.Collection` instances.
        """
        async for item in paginate(
            self._http,
            "/api/collections/shared/",
            params={"page_size": page_size, **params},
        ):
            yield Collection.model_validate(item)

    async def duplicate(self, id: str) -> Collection:
        """Duplicate an existing collection.

        Args:
            id: The UUID of the collection to duplicate.

        Returns:
            The newly created duplicate
            :class:`~adventurelog.models.collection.Collection`.
        """
        resp = await self._http.post(f"/api/collections/{id}/duplicate/")
        return Collection.model_validate(resp.json())
