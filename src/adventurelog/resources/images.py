"""ImagesResource — wraps /api/images/ endpoints."""

from __future__ import annotations

from typing import Any

from adventurelog.models.image import ContentImage
from adventurelog.resources.base import BaseResource


class ImagesResource(BaseResource):
    """Resource for the /api/images/ endpoint group.

    ContentImage records are associated with locations and other content
    objects.  The list endpoint returns a plain JSON array (non-paginated).
    """

    async def list(self) -> list[ContentImage]:
        """Return all images for the current user.

        Returns:
            List of :class:`~adventurelog.models.image.ContentImage` instances.
        """
        resp = await self._http.get("/api/images/")
        return [ContentImage.model_validate(item) for item in resp.json()]

    async def get(self, id: str) -> ContentImage:
        """Retrieve a single image by ID.

        Args:
            id: The image's UUID.

        Returns:
            The matching :class:`~adventurelog.models.image.ContentImage`.
        """
        resp = await self._http.get(f"/api/images/{id}/")
        return ContentImage.model_validate(resp.json())

    async def create(self, data: dict[str, Any]) -> ContentImage:
        """Create a new image record.

        Pass metadata fields as a dict; this sends a JSON body.

        Args:
            data: Image field data.

        Returns:
            The newly created :class:`~adventurelog.models.image.ContentImage`.
        """
        resp = await self._http.post("/api/images/", json=data)
        return ContentImage.model_validate(resp.json())

    async def update(self, id: str, data: dict[str, Any]) -> ContentImage:
        """Replace an image record (full update).

        Args:
            id: The image's UUID.
            data: Complete image field data.

        Returns:
            The updated :class:`~adventurelog.models.image.ContentImage`.
        """
        resp = await self._http.put(f"/api/images/{id}/", json=data)
        return ContentImage.model_validate(resp.json())

    async def partial_update(self, id: str, data: dict[str, Any]) -> ContentImage:
        """Partially update an image record.

        Args:
            id: The image's UUID.
            data: Fields to update.

        Returns:
            The updated :class:`~adventurelog.models.image.ContentImage`.
        """
        resp = await self._http.patch(f"/api/images/{id}/", json=data)
        return ContentImage.model_validate(resp.json())

    async def delete(self, id: str) -> None:
        """Delete an image record.

        Args:
            id: The image's UUID.
        """
        await self._http.delete(f"/api/images/{id}/")
