"""BackupResource — wraps /api/backup/ endpoints."""

from __future__ import annotations

from typing import Any

from adventurelog.resources.base import BaseResource


class BackupResource(BaseResource):
    """Resource for backup export and import endpoints.

    Covers:
    - ``GET  /api/backup/export/`` — download a full data export
    - ``POST /api/backup/import/`` — restore data from an export file
    """

    async def export(self) -> bytes:
        """Download a full backup export of the current user's data.

        Returns:
            Raw response bytes (the export file content).
        """
        resp = await self._http.get("/api/backup/export/")
        return resp.content

    async def import_backup(self, data: dict[str, Any]) -> dict[str, Any]:
        """Import (restore) data from a backup file.

        Args:
            data: Import payload or form data referencing the backup file.

        Returns:
            Raw response dict with import status.
        """
        resp = await self._http.post("/api/backup/import/", json=data)
        return dict(resp.json())
