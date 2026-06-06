"""Async pagination helpers for DRF list endpoints.

AdventureLog uses the standard Django REST Framework pagination envelope::

    {
        "count": 42,
        "next": "https://example.com/api/locations/?page=2",
        "previous": null,
        "results": [...]
    }
"""

from __future__ import annotations

from collections.abc import AsyncIterator
from typing import TYPE_CHECKING, Any

from urllib.parse import urlparse

from adventurelog.exceptions import AdventureLogError

if TYPE_CHECKING:
    from adventurelog.http import AdventureLogHTTP


async def paginate(
    http: AdventureLogHTTP,
    path: str,
    *,
    params: dict[str, Any] | None = None,
    **kwargs: Any,
) -> AsyncIterator[Any]:
    """Async generator that yields individual items from all pages.

    The ``params`` dict is sent only on the first request.  Subsequent
    requests use the absolute ``next`` URL from the DRF envelope, which
    already includes pagination query parameters.

    Args:
        http: The :class:`~adventurelog.http.AdventureLogHTTP` client.
        path: API path for the first request (e.g. ``/api/locations/``).
        params: Optional query parameters for the first request only.
        **kwargs: Additional keyword arguments forwarded to ``http.get``.

    Yields:
        Individual items (raw dicts) from every page's ``results`` list.
    """
    current_path: str | None = path
    first_request = True

    while current_path is not None:
        if first_request:
            response = await http.get(current_path, params=params, **kwargs)
            first_request = False
        else:
            # Use the full absolute URL returned by the server.
            response = await http.get(current_path, **kwargs)

        body = response.json()

        # Handle both paginated and non-paginated (plain list) responses.
        if isinstance(body, list):
            for item in body:
                yield item
            return

        results = body.get("results", [])
        for item in results:
            yield item

        next_url: str | None = body.get("next")
        if next_url:
            # The server returns an absolute URL; extract the path + query.
            current_path = _relative_path(next_url)
        else:
            current_path = None


async def fetch_page(
    http: AdventureLogHTTP,
    path: str,
    *,
    page: int | None = None,
    page_size: int | None = None,
    params: dict[str, Any] | None = None,
    **kwargs: Any,
) -> dict[str, Any]:
    """Fetch a single page and return the raw DRF envelope dict.

    Args:
        http: The :class:`~adventurelog.http.AdventureLogHTTP` client.
        path: API path (e.g. ``/api/locations/``).
        page: Page number (1-based).  Appended as ``?page=<n>``.
        page_size: Number of items per page.  Appended as ``?page_size=<n>``.
        params: Additional query parameters.
        **kwargs: Forwarded to ``http.get``.

    Returns:
        The raw response body as a dict (DRF paginated envelope or plain list
        wrapped in a synthetic envelope).
    """
    merged: dict[str, Any] = dict(params or {})
    if page is not None:
        merged["page"] = page
    if page_size is not None:
        merged["page_size"] = page_size

    response = await http.get(path, params=merged or None, **kwargs)
    body = response.json()

    # Normalise a plain-list response to the envelope shape.
    if isinstance(body, list):
        return {
            "count": len(body),
            "next": None,
            "previous": None,
            "results": body,
        }

    if not isinstance(body, dict):
        raise AdventureLogError(f"Unexpected response shape: {type(body)}")
    return body


# ------------------------------------------------------------------
# Helpers
# ------------------------------------------------------------------


def _relative_path(url: str) -> str:
    """Convert an absolute URL to a path-and-query string.

    The httpx client uses ``base_url`` for relative paths, so we strip the
    scheme and host portion and keep everything from the path onwards.

    Raises ``AdventureLogError`` if the URL has no path component, which
    would silently redirect pagination to the server root.

    >>> _relative_path("https://example.com/api/locations/?page=2")
    '/api/locations/?page=2'
    """
    parsed = urlparse(url)
    path = parsed.path
    if not path or path == "/":
        raise AdventureLogError(
            f"Pagination 'next' URL has no usable path: {url!r}"
        )
    if parsed.query:
        return f"{path}?{parsed.query}"
    return path
