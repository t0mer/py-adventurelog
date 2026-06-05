"""Authentication strategy for the AdventureLog SDK.

The server uses Django session cookie auth via django-allauth headless.
This module provides :class:`SessionAuth`, which handles the login flow,
session token injection, and logout.
"""

from __future__ import annotations

import asyncio
import logging
from typing import TYPE_CHECKING

import httpx

from adventurelog.exceptions import AuthenticationError

if TYPE_CHECKING:
    from adventurelog.config import ClientConfig
    from adventurelog.http import AdventureLogHTTP

logger = logging.getLogger(__name__)

_LOGIN_PATH = "/accounts/login/"


class SessionAuth:
    """Manages session-cookie authentication against an AdventureLog server.

    Supports two modes:

    1. **Pre-obtained token**: if ``config.session_token`` is set the value is
       injected directly into the httpx cookie jar — no HTTP login is performed.
    2. **Username + password**: the login form is submitted once; the resulting
       ``sessionid`` cookie is stored in the httpx client and used for all
       subsequent requests.

    The ``ensure_authenticated`` coroutine is idempotent — multiple calls are
    safe and will not re-submit the login form.
    """

    def __init__(self, http: AdventureLogHTTP, config: ClientConfig) -> None:
        self._http = http
        self._config = config
        self._authenticated = False
        self._login_lock: asyncio.Lock = asyncio.Lock()

    async def ensure_authenticated(self) -> None:
        """Ensure the client is authenticated.

        If ``config.session_token`` is set, inject it into the cookie jar and
        return immediately.  Otherwise perform a full login (once only).

        This method is concurrency-safe: a ``asyncio.Lock`` prevents multiple
        concurrent coroutines from each triggering a separate login call.
        """
        if self._authenticated:
            return

        async with self._login_lock:
            if self._authenticated:  # double-check after acquiring the lock
                return

            if self._config.session_token:
                self._inject_session_token(self._config.session_token)
                self._authenticated = True
                logger.debug("Using pre-obtained session token.")
                return

            await self.login()

    async def login(self) -> None:
        """Perform the Django allauth login flow.

        Steps:
        1. GET the login page to capture the ``csrftoken`` cookie.
        2. POST the login form with credentials and the CSRF token.
        3. On success the ``sessionid`` cookie is stored in the httpx client.
           The ``csrftoken`` is explicitly removed — it is not needed for API
           requests and the server clears it after login anyway.
        """
        if self._authenticated:
            return

        base = self._config.base_url

        # Step 1: get CSRF token
        login_url = f"{base}{_LOGIN_PATH}"
        try:
            get_resp = await self._http.raw_request("GET", login_url)
        except httpx.TransportError as exc:
            raise AuthenticationError(
                f"Failed to reach login page: {exc}"
            ) from exc

        csrf_token = self._http.get_cookie("csrftoken") or ""
        if not csrf_token:
            # Some deployments set the cookie name differently; try the response
            csrf_token = get_resp.cookies.get("csrftoken", "")

        logger.debug("Obtained CSRF token for login (len=%d).", len(csrf_token))

        # Step 2: POST login form
        form_data = {
            "login": self._config.username or "",
            "password": self._config.password or "",
            "csrfmiddlewaretoken": csrf_token,
        }
        headers = {
            "X-CSRFToken": csrf_token,
            "Referer": f"{base}{_LOGIN_PATH}",
            "Origin": base,
            "Content-Type": "application/x-www-form-urlencoded",
        }

        try:
            post_resp = await self._http.raw_request(
                "POST",
                login_url,
                data=form_data,
                headers=headers,
            )
        except httpx.TransportError as exc:
            raise AuthenticationError(
                f"Login request failed: {exc}"
            ) from exc

        # A successful login redirects to /dashboard (or similar).
        # The httpx client follows redirects, so we check the final URL and
        # cookie jar rather than the raw status code.
        session_id = self._http.get_cookie("sessionid")
        if not session_id:
            # Check in the response cookies as a fallback.
            session_id = post_resp.cookies.get("sessionid")

        if not session_id:
            raise AuthenticationError(
                "Login succeeded in HTTP terms but no 'sessionid' cookie was "
                f"returned. Final URL: {post_resp.url}  Status: {post_resp.status_code}"
            )

        # Remove the csrftoken — API responses clear it (Max-Age=0) and we
        # should not send it with API requests.
        self._remove_csrftoken()

        self._authenticated = True
        logger.debug(
            "Login successful. Session established. Final URL: %s", post_resp.url
        )

    async def logout(self) -> None:
        """Best-effort logout.  Errors are silently ignored."""
        try:
            await self._http.delete("/_allauth/app/v1/auth/session")
        except Exception as exc:  # noqa: BLE001
            logger.debug("Logout error (ignored): %s", exc)
        finally:
            self._authenticated = False

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _inject_session_token(self, token: str) -> None:
        """Inject a ``sessionid`` cookie value directly into the client jar."""
        self._http.set_cookie(
            "sessionid", token, domain=_domain_from_base(self._config.base_url)
        )

    def _remove_csrftoken(self) -> None:
        """Delete the ``csrftoken`` cookie from the client jar."""
        self._http.delete_cookie("csrftoken")


def _domain_from_base(base_url: str) -> str:
    """Extract the host (without port) from a base URL string."""
    # base_url has already been stripped of trailing slash.
    # e.g. "https://travel.example.com" → "travel.example.com"
    without_scheme = base_url.split("://", 1)[-1]
    return without_scheme.split("/")[0].split(":")[0]
