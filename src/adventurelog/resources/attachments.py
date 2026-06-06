"""AttachmentsResource — wraps /api/attachments/ endpoints."""

from __future__ import annotations

from typing import Any

from adventurelog.resources.base import BaseResource


class AttachmentsResource(BaseResource):
    """Resource for the /api/attachments/ endpoint group.

    Attachments are files (PDFs, documents, etc.) associated with locations
    or collections.  The list endpoint returns a plain JSON array
    (non-paginated).
    """

    async def list(self) -> list[dict[str, Any]]:
        """Return all attachments for the current user.

        Returns:
            List of raw attachment dicts.
        """
        resp = await self._http.get("/api/attachments/")
        return list(resp.json())

    async def get(self, id: str) -> dict[str, Any]:
        """Retrieve a single attachment by ID.

        Args:
            id: The attachment's UUID.

        Returns:
            Raw attachment dict.
        """
        resp = await self._http.get(f"/api/attachments/{id}/")
        return dict(resp.json())

    async def create(self, data: dict[str, Any]) -> dict[str, Any]:
        """Create a new attachment record.

        Args:
            data: Attachment field data.

        Returns:
            Raw dict for the newly created attachment.
        """
        resp = await self._http.post("/api/attachments/", json=data)
        return dict(resp.json())

    async def update(self, id: str, data: dict[str, Any]) -> dict[str, Any]:
        """Replace an attachment record (full update).

        Args:
            id: The attachment's UUID.
            data: Complete attachment field data.

        Returns:
            Raw dict for the updated attachment.
        """
        resp = await self._http.put(f"/api/attachments/{id}/", json=data)
        return dict(resp.json())

    async def partial_update(self, id: str, data: dict[str, Any]) -> dict[str, Any]:
        """Partially update an attachment record.

        Args:
            id: The attachment's UUID.
            data: Fields to update.

        Returns:
            Raw dict for the updated attachment.
        """
        resp = await self._http.patch(f"/api/attachments/{id}/", json=data)
        return dict(resp.json())

    async def delete(self, id: str) -> None:
        """Delete an attachment record.

        Args:
            id: The attachment's UUID.
        """
        await self._http.delete(f"/api/attachments/{id}/")
