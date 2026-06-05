"""User, ImmichIntegration, APIKey, and APIKeyCreate models."""

from __future__ import annotations

from datetime import datetime

from pydantic import ConfigDict

from adventurelog.models.common import AdventureLogModel


class CustomUserDetails(AdventureLogModel):
    """Detailed user profile information."""

    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    pk: int | None = None
    profile_pic: str | None = None  # URL
    uuid: str | None = None
    public_profile: bool | None = None
    username: str | None = None
    email: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    date_joined: datetime | None = None
    is_staff: bool | None = None
    disable_password: bool | None = None
    measurement_system: str | None = None
    default_currency: str | None = None
    map_style: str | None = None
    has_password: bool | None = None


class ImmichIntegration(AdventureLogModel):
    """Immich photo server integration configuration."""

    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    id: int | None = None
    server_url: str | None = None
    api_key: str | None = None  # key prefix only returned in GET
    copy_locally: bool | None = None
    user: int | str | None = None


class APIKey(AdventureLogModel):
    """An API key for programmatic access."""

    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    id: int | None = None
    name: str | None = None
    key_prefix: str | None = None
    created_at: datetime | None = None
    last_used_at: datetime | None = None


class APIKeyCreate(AdventureLogModel):
    """Request body for creating a new API key."""

    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    name: str
