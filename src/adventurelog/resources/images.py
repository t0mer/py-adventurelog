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

    async def fetch_from_url(self, data: dict[str, Any]) -> ContentImage:
        """Fetch and create an image record from a remote URL.

        Args:
            data: Dict containing the image URL and any associated metadata.

        Returns:
            The newly created :class:`~adventurelog.models.image.ContentImage`.
        """
        resp = await self._http.post("/api/images/fetch_from_url/", json=data)
        return ContentImage.model_validate(resp.json())

    async def import_from_urls(self, data: dict[str, Any]) -> list[ContentImage]:
        """Bulk-import images from a list of remote URLs.

        Args:
            data: Dict containing a list of URLs and associated metadata.

        Returns:
            List of :class:`~adventurelog.models.image.ContentImage` instances.
        """
        resp = await self._http.post("/api/images/import_from_urls/", json=data)
        return [ContentImage.model_validate(item) for item in resp.json()]

    async def image_delete(self, id: str) -> dict[str, Any]:
        """Delete the image file associated with an image record.

        Args:
            id: The image's UUID.

        Returns:
            Raw response dict.
        """
        resp = await self._http.post(f"/api/images/{id}/image_delete/")
        return dict(resp.json())

    async def toggle_primary(self, id: str) -> ContentImage:
        """Toggle the primary flag on an image.

        Args:
            id: The image's UUID.

        Returns:
            The updated :class:`~adventurelog.models.image.ContentImage`.
        """
        resp = await self._http.post(f"/api/images/{id}/toggle_primary/")
        return ContentImage.model_validate(resp.json())
