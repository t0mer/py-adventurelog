"""CategoriesResource — wraps /api/categories/ endpoints."""

from __future__ import annotations

from typing import Any

from adventurelog.models.category import Category
from adventurelog.resources.base import BaseResource


class CategoriesResource(BaseResource):
    """Resource for the /api/categories/ endpoint group.

    Categories classify locations (e.g. Restaurant, Hotel, Park).  The list
    endpoint returns a plain JSON array (non-paginated).
    """

    async def list(self) -> list[Category]:
        """Return all location categories.

        Returns:
            List of :class:`~adventurelog.models.category.Category` instances.
        """
        resp = await self._http.get("/api/categories/")
        return [Category.model_validate(item) for item in resp.json()]

    async def get(self, id: str) -> Category:
        """Retrieve a single category by ID.

        Args:
            id: The category's UUID.

        Returns:
            The matching :class:`~adventurelog.models.category.Category`.
        """
        resp = await self._http.get(f"/api/categories/{id}/")
        return Category.model_validate(resp.json())

    async def create(self, data: dict[str, Any]) -> Category:
        """Create a new category.

        Args:
            data: Category field data.

        Returns:
            The newly created :class:`~adventurelog.models.category.Category`.
        """
        resp = await self._http.post("/api/categories/", json=data)
        return Category.model_validate(resp.json())

    async def update(self, id: str, data: dict[str, Any]) -> Category:
        """Replace a category (full update).

        Args:
            id: The category's UUID.
            data: Complete category field data.

        Returns:
            The updated :class:`~adventurelog.models.category.Category`.
        """
        resp = await self._http.put(f"/api/categories/{id}/", json=data)
        return Category.model_validate(resp.json())

    async def partial_update(self, id: str, data: dict[str, Any]) -> Category:
        """Partially update a category.

        Args:
            id: The category's UUID.
            data: Fields to update.

        Returns:
            The updated :class:`~adventurelog.models.category.Category`.
        """
        resp = await self._http.patch(f"/api/categories/{id}/", json=data)
        return Category.model_validate(resp.json())

    async def delete(self, id: str) -> None:
        """Delete a category.

        Args:
            id: The category's UUID.
        """
        await self._http.delete(f"/api/categories/{id}/")
