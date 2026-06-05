"""Exception hierarchy for the AdventureLog SDK."""

from __future__ import annotations


class AdventureLogError(Exception):
    """Base exception for all AdventureLog SDK errors."""


class AuthenticationError(AdventureLogError):
    """Raised when authentication fails (HTTP 401)."""


class PermissionDenied(AdventureLogError):
    """Raised when the authenticated user lacks permission (HTTP 403)."""


class NotFoundError(AdventureLogError):
    """Raised when a requested resource is not found (HTTP 404)."""


class ValidationError(AdventureLogError):
    """Raised on bad request or validation failure (HTTP 400/422).

    Carries structured field errors from DRF when available.
    """

    def __init__(
        self,
        message: str,
        field_errors: dict[str, list[str]] | None = None,
    ) -> None:
        super().__init__(message)
        self.field_errors: dict[str, list[str]] = field_errors or {}


class RateLimitError(AdventureLogError):
    """Raised when the server rate-limits the client (HTTP 429)."""


class ServerError(AdventureLogError):
    """Raised on 5xx responses from the server."""


class APIConnectionError(AdventureLogError):
    """Raised on network or transport errors (wraps httpx transport exceptions)."""
