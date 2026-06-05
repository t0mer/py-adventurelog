"""Client configuration for the AdventureLog SDK."""

from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass
class ClientConfig:
    """Configuration for an AdventureLog client instance.

    At least one of ``(username + password)`` or ``session_token`` must be
    provided.  ``session_token`` is the raw value of the ``sessionid`` cookie
    obtained from a prior login.
    """

    base_url: str
    """Server base URL, no trailing slash (e.g. ``https://travel.example.com``)."""

    username: str | None = None
    """AdventureLog username.  Required when ``session_token`` is not set."""

    password: str | None = None
    """AdventureLog password.  Required when ``session_token`` is not set."""

    session_token: str | None = None
    """Pre-obtained ``sessionid`` cookie value.  Skips login when provided."""

    timeout: float = 30.0
    """Default request timeout in seconds."""

    max_retries: int = 3
    """Maximum number of retries for idempotent requests on 5xx / transport errors."""

    # Internal: mutable defaults need field() with default_factory when they are
    # mutable, but these are scalars so plain defaults are fine.

    def __post_init__(self) -> None:
        self.base_url = self.base_url.rstrip("/")
        if not self.session_token and not (self.username and self.password):
            raise ValueError(
                "ClientConfig requires either 'session_token' "
                "or both 'username' and 'password'."
            )

    @classmethod
    def from_env(cls) -> ClientConfig:
        """Create a ``ClientConfig`` by reading environment variables.

        Variables read:
        - ``ADVENTURELOG_BASE_URL`` (required)
        - ``ADVENTURELOG_USERNAME``
        - ``ADVENTURELOG_PASSWORD``
        - ``ADVENTURELOG_SESSION_TOKEN``
        """
        base_url = os.environ.get("ADVENTURELOG_BASE_URL", "").strip()
        if not base_url:
            raise ValueError(
                "ADVENTURELOG_BASE_URL environment variable is required."
            )
        return cls(
            base_url=base_url,
            username=os.environ.get("ADVENTURELOG_USERNAME") or None,
            password=os.environ.get("ADVENTURELOG_PASSWORD") or None,
            session_token=os.environ.get("ADVENTURELOG_SESSION_TOKEN") or None,
        )
