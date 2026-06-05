"""py-adventurelog — Async Python SDK for AdventureLog."""

from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("py-adventurelog")
except PackageNotFoundError:
    __version__ = "0.0.0"

from adventurelog.client import AdventureLog, AsyncAdventureLog  # noqa: F401
from adventurelog.exceptions import (  # noqa: F401
    AdventureLogError,
    APIConnectionError,
    AuthenticationError,
    NotFoundError,
    PermissionDenied,
    RateLimitError,
    ServerError,
    ValidationError,
)

__all__ = [
    "__version__",
    # Clients
    "AsyncAdventureLog",
    "AdventureLog",
    # Exceptions
    "AdventureLogError",
    "APIConnectionError",
    "AuthenticationError",
    "NotFoundError",
    "PermissionDenied",
    "RateLimitError",
    "ServerError",
    "ValidationError",
]
