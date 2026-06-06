"""Async HTTP transport wrapper for the AdventureLog SDK."""

from __future__ import annotations

import asyncio
import logging
from importlib.metadata import PackageNotFoundError
from importlib.metadata import version as _pkg_version
from typing import Any

import httpx

from adventurelog.config import ClientConfig
from adventurelog.exceptions import (
    APIConnectionError,
    AuthenticationError,
    NotFoundError,
    PermissionDenied,
    RateLimitError,
    ServerError,
    ValidationError,
)

try:
    _VERSION = _pkg_version("py-adventurelog")
except PackageNotFoundError:
    _VERSION = "0.0.0"
_USER_AGENT = f"py-adventurelog/{_VERSION}"
_IDEMPOTENT_METHODS = frozenset({"GET", "HEAD", "OPTIONS", "PUT", "DELETE"})

logger = logging.getLogger(__name__)


class AdventureLogHTTP:
    """Async HTTP client wrapping :class:`httpx.AsyncClient`.

    Handles URL construction, default headers, error mapping, and
    retry logic for idempotent requests.
    """

    def __init__(self, config: ClientConfig) -> None:
        self._config = config
        self._client = httpx.AsyncClient(
            base_url=config.base_url,
            timeout=config.timeout,
            headers={
                "Accept": "application/json",
                "User-Agent": _USER_AGENT,
            },
            follow_redirects=True,
            verify=True,  # explicit: never disable TLS certificate verification
        )

    # ------------------------------------------------------------------
    # Context-manager support
    # ------------------------------------------------------------------

    async def __aenter__(self) -> AdventureLogHTTP:
        await self._client.__aenter__()
        return self

    async def __aexit__(self, *args: Any) -> None:
        await self._client.__aexit__(*args)

    async def aclose(self) -> None:
        """Close the underlying httpx client."""
        await self._client.aclose()

    # ------------------------------------------------------------------
    # Public request methods
    # ------------------------------------------------------------------

    async def get(self, path: str, **kwargs: Any) -> httpx.Response:
        """Send a GET request."""
        return await self._request("GET", path, **kwargs)

    async def post(self, path: str, **kwargs: Any) -> httpx.Response:
        """Send a POST request."""
        return await self._request("POST", path, **kwargs)

    async def put(self, path: str, **kwargs: Any) -> httpx.Response:
        """Send a PUT request."""
        return await self._request("PUT", path, **kwargs)

    async def patch(self, path: str, **kwargs: Any) -> httpx.Response:
        """Send a PATCH request."""
        return await self._request("PATCH", path, **kwargs)

    async def delete(self, path: str, **kwargs: Any) -> httpx.Response:
        """Send a DELETE request."""
        return await self._request("DELETE", path, **kwargs)

    # ------------------------------------------------------------------
    # Cookie management
    # ------------------------------------------------------------------

    def set_cookie(self, name: str, value: str, *, domain: str = "") -> None:
        """Set a cookie on the underlying httpx client jar."""
        self._client.cookies.set(name, value, domain=domain or None)

    def delete_cookie(self, name: str) -> None:
        """Remove a cookie from the underlying httpx client jar."""
        try:
            del self._client.cookies[name]
        except KeyError:
            pass

    def get_cookie(self, name: str) -> str | None:
        """Return a cookie value from the client jar, or ``None`` if absent."""
        return self._client.cookies.get(name)

    async def raw_request(self, method: str, url: str, **kwargs: Any) -> httpx.Response:
        """Send a request using a full URL, bypassing base_url joining and retries.

        Intended for pre-auth calls (e.g. the login form) where the caller
        already holds the full URL and retry logic is not appropriate.
        """
        return await self._client.request(method, url, **kwargs)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    async def _request(
        self, method: str, path: str, **kwargs: Any
    ) -> httpx.Response:
        """Execute an HTTP request with retry logic and error mapping.

        Retries up to ``config.max_retries`` times on transport errors or 5xx
        responses, but only for idempotent HTTP methods.
        """
        retries = (
            self._config.max_retries
            if method.upper() in _IDEMPOTENT_METHODS
            else 0
        )
        attempt = 0
        last_exc: Exception | None = None

        while True:
            try:
                response = await self._client.request(method, path, **kwargs)
                self._raise_for_status(response)
                return response
            except ServerError as exc:
                last_exc = exc
                if attempt >= retries:
                    raise
                delay = min(0.5 * (2**attempt), 30.0)
                logger.debug(
                    "Request %s %s failed (attempt %d/%d): %s — retrying in %.1fs",
                    method,
                    path,
                    attempt + 1,
                    retries + 1,
                    exc,
                    delay,
                )
                await asyncio.sleep(delay)
                attempt += 1
            except httpx.TransportError as exc:
                last_exc = exc
                if attempt >= retries or method.upper() not in _IDEMPOTENT_METHODS:
                    raise APIConnectionError(
                        f"Connection error on {method} {path}: {exc}"
                    ) from exc
                delay = min(0.5 * (2**attempt), 30.0)
                logger.debug(
                    "Transport error on %s %s (attempt %d/%d) — retrying in %.1fs",
                    method,
                    path,
                    attempt + 1,
                    retries + 1,
                    delay,
                )
                await asyncio.sleep(delay)
                attempt += 1

        # unreachable, but satisfies type checker
        assert last_exc is not None
        raise last_exc

    def _raise_for_status(self, response: httpx.Response) -> None:
        """Map HTTP error codes to SDK exceptions."""
        status = response.status_code
        if status < 400:
            return

        # Try to extract a human-readable message from the response body.
        try:
            body = response.json()
        except ValueError:
            body = {}

        detail = _extract_detail(body) or response.text

        if status == 400 or status == 422:
            field_errors = _extract_field_errors(body)
            raise ValidationError(
                f"Validation error ({status}): {detail}", field_errors=field_errors
            )
        if status == 401:
            raise AuthenticationError(f"Authentication required: {detail}")
        if status == 403:
            raise PermissionDenied(f"Permission denied: {detail}")
        if status == 404:
            raise NotFoundError(f"Not found: {detail}")
        if status == 429:
            raise RateLimitError(f"Rate limit exceeded: {detail}")
        if status >= 500:
            raise ServerError(f"Server error ({status}): {detail}")
        # Other 4xx
        raise ValidationError(f"Client error ({status}): {detail}")


# ------------------------------------------------------------------
# Helpers for error body parsing
# ------------------------------------------------------------------


def _extract_detail(body: Any) -> str:
    """Return a flat string from a DRF error body."""
    if isinstance(body, dict):
        return str(body.get("detail", "") or body.get("error", ""))
    if isinstance(body, list):
        return "; ".join(str(item) for item in body)
    return str(body) if body else ""


def _extract_field_errors(body: Any) -> dict[str, list[str]]:
    """Parse DRF field-level errors into ``{field: [messages]}``."""
    if not isinstance(body, dict):
        return {}
    errors: dict[str, list[str]] = {}
    for key, value in body.items():
        if key in ("detail", "non_field_errors"):
            continue
        if isinstance(value, list):
            errors[key] = [str(v) for v in value]
        elif isinstance(value, str):
            errors[key] = [value]
        # nested dicts (e.g. nested serializer errors) are flattened
        elif isinstance(value, dict):
            for sub_key, sub_val in value.items():
                flat_key = f"{key}.{sub_key}"
                if isinstance(sub_val, list):
                    errors[flat_key] = [str(v) for v in sub_val]
                else:
                    errors[flat_key] = [str(sub_val)]
    # also capture non_field_errors
    if "non_field_errors" in body:
        nfe = body["non_field_errors"]
        errors["non_field_errors"] = (
            [str(v) for v in nfe] if isinstance(nfe, list) else [str(nfe)]
        )
    return errors
