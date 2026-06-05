"""Base resource class shared by all resource modules."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from adventurelog.http import AdventureLogHTTP


class BaseResource:
    """Base class for all AdventureLog API resource wrappers.

    Each concrete resource subclass holds a reference to the shared HTTP
    client and exposes async methods that map to individual API endpoints.
    """

    def __init__(self, http: AdventureLogHTTP) -> None:
        self._http = http
