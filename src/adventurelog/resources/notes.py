"""NotesResource — wraps /api/notes/ endpoints."""

from __future__ import annotations

from typing import Any

from adventurelog.models.note import Note
from adventurelog.resources.base import BaseResource


class NotesResource(BaseResource):
    """Resource for the /api/notes/ endpoint group.

    Notes are text entries associated with collections.  The /api/notes/
    and /api/notes/all/ endpoints both return plain JSON arrays.
    """

    async def list(self) -> list[Note]:
        """Return notes for the current user's collections.

        Returns:
            List of :class:`~adventurelog.models.note.Note` instances.
        """
        resp = await self._http.get("/api/notes/")
        return [Note.model_validate(item) for item in resp.json()]

    async def all_notes(self) -> list[Note]:
        """Return all notes including those from shared collections.

        Returns:
            List of :class:`~adventurelog.models.note.Note` instances.
        """
        resp = await self._http.get("/api/notes/all/")
        return [Note.model_validate(item) for item in resp.json()]

    async def get(self, id: str) -> Note:
        """Retrieve a single note by ID.

        Args:
            id: The note's UUID.

        Returns:
            The matching :class:`~adventurelog.models.note.Note`.
        """
        resp = await self._http.get(f"/api/notes/{id}/")
        return Note.model_validate(resp.json())

    async def create(self, data: dict[str, Any]) -> Note:
        """Create a new note.

        Args:
            data: Note field data.

        Returns:
            The newly created :class:`~adventurelog.models.note.Note`.
        """
        resp = await self._http.post("/api/notes/", json=data)
        return Note.model_validate(resp.json())

    async def update(self, id: str, data: dict[str, Any]) -> Note:
        """Replace a note (full update).

        Args:
            id: The note's UUID.
            data: Complete note field data.

        Returns:
            The updated :class:`~adventurelog.models.note.Note`.
        """
        resp = await self._http.put(f"/api/notes/{id}/", json=data)
        return Note.model_validate(resp.json())

    async def partial_update(self, id: str, data: dict[str, Any]) -> Note:
        """Partially update a note.

        Args:
            id: The note's UUID.
            data: Fields to update.

        Returns:
            The updated :class:`~adventurelog.models.note.Note`.
        """
        resp = await self._http.patch(f"/api/notes/{id}/", json=data)
        return Note.model_validate(resp.json())

    async def delete(self, id: str) -> None:
        """Delete a note.

        Args:
            id: The note's UUID.
        """
        await self._http.delete(f"/api/notes/{id}/")
