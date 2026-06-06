"""IntegrationsResource — wraps /api/integrations/ endpoints (Immich, Strava, Wanderer)."""

from __future__ import annotations

from typing import Any

from adventurelog.resources.base import BaseResource


class IntegrationsResource(BaseResource):
    """Resource for third-party integration endpoints.

    Covers three integration providers:

    **Immich** (self-hosted photo management):
    - ``/api/integrations/immich/``
    - ``/api/integrations/immich/albums/``
    - ``/api/integrations/immich/search/``
    - ``/api/integrations/immich/{id}/``
    - ``/api/integrations/immich/{integration_id}/get/{imageid}/``

    **Strava** (fitness activity tracking):
    - ``/api/integrations/strava/activities/``
    - ``/api/integrations/strava/authorize/``
    - ``/api/integrations/strava/callback/``
    - ``/api/integrations/strava/disable/``

    **Wanderer** (trail/route tracking):
    - ``/api/integrations/wanderer/``
    - ``/api/integrations/wanderer/trails/``
    - ``/api/integrations/wanderer/disable/``
    - ``/api/integrations/wanderer/refresh/``
    - ``/api/integrations/wanderer/{id}/``
    """

    # ------------------------------------------------------------------
    # General
    # ------------------------------------------------------------------

    async def list(self) -> list[dict[str, Any]]:
        """Return all configured integrations for the current user.

        Returns:
            List of raw integration dicts.
        """
        resp = await self._http.get("/api/integrations/")
        return list(resp.json())

    # ------------------------------------------------------------------
    # Immich
    # ------------------------------------------------------------------

    async def immich_list(self) -> list[dict[str, Any]]:
        """Return all Immich integration configurations.

        Returns:
            List of raw Immich integration dicts.
        """
        resp = await self._http.get("/api/integrations/immich/")
        return list(resp.json())

    async def immich_create(self, data: dict[str, Any]) -> dict[str, Any]:
        """Create a new Immich integration.

        Args:
            data: Immich integration config (server URL, API key, etc.).

        Returns:
            Raw dict for the newly created integration.
        """
        resp = await self._http.post("/api/integrations/immich/", json=data)
        return dict(resp.json())

    async def immich_get(self, id: str) -> dict[str, Any]:
        """Retrieve a single Immich integration by ID.

        Args:
            id: The integration's UUID.

        Returns:
            Raw integration dict.
        """
        resp = await self._http.get(f"/api/integrations/immich/{id}/")
        return dict(resp.json())

    async def immich_update(self, id: str, data: dict[str, Any]) -> dict[str, Any]:
        """Replace an Immich integration (full update).

        Args:
            id: The integration's UUID.
            data: Complete integration field data.

        Returns:
            Raw dict for the updated integration.
        """
        resp = await self._http.put(f"/api/integrations/immich/{id}/", json=data)
        return dict(resp.json())

    async def immich_partial_update(
        self, id: str, data: dict[str, Any]
    ) -> dict[str, Any]:
        """Partially update an Immich integration.

        Args:
            id: The integration's UUID.
            data: Fields to update.

        Returns:
            Raw dict for the updated integration.
        """
        resp = await self._http.patch(f"/api/integrations/immich/{id}/", json=data)
        return dict(resp.json())

    async def immich_delete(self, id: str) -> None:
        """Delete an Immich integration.

        Args:
            id: The integration's UUID.
        """
        await self._http.delete(f"/api/integrations/immich/{id}/")

    async def immich_albums(self) -> list[dict[str, Any]]:
        """Return all Immich albums available via the configured integration.

        Returns:
            List of raw album dicts.
        """
        resp = await self._http.get("/api/integrations/immich/albums/")
        return list(resp.json())

    async def immich_album(self, album_id: str) -> dict[str, Any]:
        """Retrieve a single Immich album by ID.

        Args:
            album_id: The Immich album ID.

        Returns:
            Raw album dict.
        """
        resp = await self._http.get(f"/api/integrations/immich/albums/{album_id}/")
        return dict(resp.json())

    async def immich_search(self, **params: Any) -> dict[str, Any]:
        """Search Immich assets.

        Args:
            **params: Query parameters forwarded to the search endpoint.

        Returns:
            Raw response dict with search results.
        """
        resp = await self._http.get(
            "/api/integrations/immich/search/", params=params or None
        )
        return dict(resp.json())

    async def immich_get_image(
        self, integration_id: str, image_id: str
    ) -> dict[str, Any]:
        """Retrieve a specific Immich image via an integration.

        Args:
            integration_id: The Immich integration's UUID.
            image_id: The Immich image ID.

        Returns:
            Raw image dict.
        """
        resp = await self._http.get(
            f"/api/integrations/immich/{integration_id}/get/{image_id}/"
        )
        return dict(resp.json())

    # ------------------------------------------------------------------
    # Strava
    # ------------------------------------------------------------------

    async def strava_activities(self) -> list[dict[str, Any]]:
        """Return Strava activities imported from the connected account.

        Returns:
            List of raw activity dicts.
        """
        resp = await self._http.get("/api/integrations/strava/activities/")
        return list(resp.json())

    async def strava_activity(self, activity_id: str) -> dict[str, Any]:
        """Retrieve a single Strava activity by ID.

        Args:
            activity_id: The Strava activity ID.

        Returns:
            Raw activity dict.
        """
        resp = await self._http.get(
            f"/api/integrations/strava/activities/{activity_id}/"
        )
        return dict(resp.json())

    async def strava_authorize(self) -> dict[str, Any]:
        """Initiate the Strava OAuth authorization flow.

        Returns:
            Raw response dict (typically contains an authorization URL).
        """
        resp = await self._http.get("/api/integrations/strava/authorize/")
        return dict(resp.json())

    async def strava_callback(self, **params: Any) -> dict[str, Any]:
        """Handle the Strava OAuth callback.

        Args:
            **params: Query parameters from the OAuth callback (code, state, etc.).

        Returns:
            Raw response dict with token or status info.
        """
        resp = await self._http.get(
            "/api/integrations/strava/callback/", params=params or None
        )
        return dict(resp.json())

    async def strava_disable(self) -> dict[str, Any]:
        """Disconnect the Strava integration.

        Returns:
            Raw response dict.
        """
        resp = await self._http.post("/api/integrations/strava/disable/")
        return dict(resp.json())

    # ------------------------------------------------------------------
    # Wanderer
    # ------------------------------------------------------------------

    async def wanderer_create(self, data: dict[str, Any]) -> dict[str, Any]:
        """Create / connect the Wanderer integration.

        Args:
            data: Wanderer connection config (server URL, credentials, etc.).

        Returns:
            Raw dict for the created integration.
        """
        resp = await self._http.post("/api/integrations/wanderer/", json=data)
        return dict(resp.json())

    async def wanderer_update(self, id: str, data: dict[str, Any]) -> dict[str, Any]:
        """Update the Wanderer integration config.

        Args:
            id: The Wanderer integration's UUID.
            data: Updated config fields.

        Returns:
            Raw dict for the updated integration.
        """
        resp = await self._http.put(f"/api/integrations/wanderer/{id}/", json=data)
        return dict(resp.json())

    async def wanderer_trails(self) -> list[dict[str, Any]]:
        """Return trails imported from Wanderer.

        Returns:
            List of raw trail dicts.
        """
        resp = await self._http.get("/api/integrations/wanderer/trails/")
        return list(resp.json())

    async def wanderer_refresh(self) -> dict[str, Any]:
        """Refresh the Wanderer integration (re-sync trails).

        Returns:
            Raw response dict with refresh status.
        """
        resp = await self._http.post("/api/integrations/wanderer/refresh/")
        return dict(resp.json())

    async def wanderer_disable(self) -> dict[str, Any]:
        """Disconnect the Wanderer integration.

        Returns:
            Raw response dict.
        """
        resp = await self._http.post("/api/integrations/wanderer/disable/")
        return dict(resp.json())
