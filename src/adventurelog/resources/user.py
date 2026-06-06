"""UserResource — wraps user profile and API key endpoints."""

from __future__ import annotations

from typing import Any

from adventurelog.models.user import APIKey, CustomUserDetails
from adventurelog.resources.base import BaseResource


class UserResource(BaseResource):
    """Resource for user profile and API key management endpoints.

    Covers:
    - ``/auth/user-metadata/`` — current user profile
    - ``/auth/update-user/`` — update user profile
    - ``/auth/api-keys/`` — API key management
    """

    async def me(self) -> CustomUserDetails:
        """Return the current authenticated user's profile.

        Returns:
            :class:`~adventurelog.models.user.CustomUserDetails` for the
            currently authenticated user.
        """
        resp = await self._http.get("/auth/user-metadata/")
        return CustomUserDetails.model_validate(resp.json())

    async def update_profile(self, data: dict[str, Any]) -> CustomUserDetails:
        """Partially update the current user's profile.

        Args:
            data: Profile fields to update (e.g. ``first_name``,
                ``measurement_system``, ``default_currency``).

        Returns:
            The updated :class:`~adventurelog.models.user.CustomUserDetails`.
        """
        resp = await self._http.patch("/auth/update-user/", json=data)
        return CustomUserDetails.model_validate(resp.json())

    async def api_keys(self) -> list[APIKey]:
        """Return all API keys for the current user.

        Note: the full key value is never returned after initial creation.
        Only the key prefix and metadata are returned here.

        Returns:
            List of :class:`~adventurelog.models.user.APIKey` instances.
        """
        resp = await self._http.get("/auth/api-keys/")
        return [APIKey.model_validate(item) for item in resp.json()]

    async def create_api_key(self, name: str) -> dict[str, Any]:
        """Create a new API key.

        The full key is returned **once** in the response and cannot be
        retrieved again.  The caller is responsible for storing it.

        Args:
            name: A human-readable label for this API key.

        Returns:
            Raw response dict containing the full key (only shown once)
            along with metadata fields.
        """
        resp = await self._http.post("/auth/api-keys/", json={"name": name})
        return dict(resp.json())

    async def delete_api_key(self, id: str) -> None:
        """Revoke and delete an API key.

        Args:
            id: The API key's UUID.
        """
        await self._http.delete(f"/auth/api-keys/{id}/")

    async def get_user(self, username: str) -> CustomUserDetails:
        """Retrieve a user's public profile by username.

        Args:
            username: The target user's username.

        Returns:
            :class:`~adventurelog.models.user.CustomUserDetails` for that user.
        """
        resp = await self._http.get(f"/auth/user/{username}/")
        return CustomUserDetails.model_validate(resp.json())

    async def users(self) -> list[CustomUserDetails]:
        """Return all users (admin use).

        Returns:
            List of :class:`~adventurelog.models.user.CustomUserDetails`.
        """
        resp = await self._http.get("/auth/users/")
        return [CustomUserDetails.model_validate(item) for item in resp.json()]

    async def is_registration_disabled(self) -> dict[str, Any]:
        """Check whether public registration is disabled on this server.

        Returns:
            Raw response dict (e.g. ``{"is_disabled": true}``).
        """
        resp = await self._http.get("/auth/is-registration-disabled/")
        return dict(resp.json())

    async def social_providers(self) -> list[dict[str, Any]]:
        """Return configured social authentication providers.

        Returns:
            List of raw provider dicts.
        """
        resp = await self._http.get("/auth/social-providers/")
        return list(resp.json())

    async def disable_password(self) -> dict[str, Any]:
        """Disable password-based login for the current user.

        Returns:
            Raw response dict.
        """
        resp = await self._http.post("/auth/disable-password/")
        return dict(resp.json())

    async def enable_password(self) -> None:
        """Re-enable password-based login for the current user."""
        await self._http.delete("/auth/disable-password/")

    async def mobile_qr(self) -> dict[str, Any]:
        """Retrieve the mobile QR login code for the current user.

        Returns:
            Raw response dict containing the QR payload.
        """
        resp = await self._http.get("/auth/mobile-qr/")
        return dict(resp.json())

    async def create_mobile_qr(self) -> dict[str, Any]:
        """Generate a new mobile QR login code.

        Returns:
            Raw response dict containing the new QR payload.
        """
        resp = await self._http.post("/auth/mobile-qr/")
        return dict(resp.json())

    async def delete_mobile_qr(self) -> None:
        """Delete the mobile QR login code for the current user."""
        await self._http.delete("/auth/mobile-qr/")
