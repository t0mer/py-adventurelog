"""py-adventurelog — Async Python SDK for AdventureLog."""

from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("py-adventurelog")
except PackageNotFoundError:
    __version__ = "0.0.0"

# TODO: uncomment once client.py is implemented (Task 4)
# from adventurelog.client import AsyncAdventureLog, AdventureLog  # noqa: E402, F401

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
