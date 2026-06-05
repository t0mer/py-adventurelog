"""Tests for SessionAuth: login flow, token injection, concurrency, logout."""

from __future__ import annotations

import asyncio

import httpx
import pytest
import respx

from adventurelog.auth import SessionAuth
from adventurelog.config import ClientConfig
from adventurelog.exceptions import AuthenticationError
from adventurelog.http import AdventureLogHTTP

BASE_URL = "https://test.example.com"
LOGIN_URL = f"{BASE_URL}/accounts/login/"
LOGOUT_PATH = "/_allauth/app/v1/auth/session"


def _make_config(*, session_token: str | None = None) -> ClientConfig:
    if session_token:
        return ClientConfig(base_url=BASE_URL, session_token=session_token)
    return ClientConfig(base_url=BASE_URL, username="testuser", password="testpass")


def _login_get_response() -> httpx.Response:
    """Simulated GET /accounts/login/ that sets csrftoken cookie."""
    return httpx.Response(
        200,
        html="<form></form>",
        headers={"Set-Cookie": "csrftoken=csrfvalue123; Path=/"},
    )


def _login_post_response() -> httpx.Response:
    """Simulated POST /accounts/login/ that sets sessionid cookie.

    We use 200 (not 302) here to avoid httpx following the redirect to '/'
    which would require an additional mock.  The auth code checks the cookie
    jar, not the status code, so 200 is equivalent for testing purposes.
    """
    return httpx.Response(
        200,
        html="<html>Login OK</html>",
        headers={"Set-Cookie": "sessionid=sessionvalue456; Path=/"},
    )


class TestLoginFlow:
    @respx.mock
    async def test_successful_login_sets_sessionid(self) -> None:
        """A full username+password login flow should result in a sessionid cookie."""
        respx.get(LOGIN_URL).mock(return_value=_login_get_response())
        respx.post(LOGIN_URL).mock(return_value=_login_post_response())

        cfg = _make_config()
        async with AdventureLogHTTP(cfg) as http:
            auth = SessionAuth(http, cfg)
            await auth.ensure_authenticated()
            assert http.get_cookie("sessionid") is not None

    @respx.mock
    async def test_successful_login_sets_authenticated_flag(self) -> None:
        respx.get(LOGIN_URL).mock(return_value=_login_get_response())
        respx.post(LOGIN_URL).mock(return_value=_login_post_response())

        cfg = _make_config()
        async with AdventureLogHTTP(cfg) as http:
            auth = SessionAuth(http, cfg)
            assert not auth._authenticated
            await auth.ensure_authenticated()
            assert auth._authenticated

    @respx.mock
    async def test_login_sends_csrf_token_in_form(self) -> None:
        """The POST should include csrfmiddlewaretoken from the GET response cookie."""
        post_request_body: dict[str, str] = {}

        def capture_post(request: httpx.Request) -> httpx.Response:
            # Parse form body
            content = request.content.decode()
            for part in content.split("&"):
                if "=" in part:
                    k, v = part.split("=", 1)
                    post_request_body[k] = v
            return _login_post_response()

        respx.get(LOGIN_URL).mock(return_value=_login_get_response())
        respx.post(LOGIN_URL).mock(side_effect=capture_post)

        cfg = _make_config()
        async with AdventureLogHTTP(cfg) as http:
            auth = SessionAuth(http, cfg)
            await auth.login()

        assert "csrfmiddlewaretoken" in post_request_body

    @respx.mock
    async def test_login_raises_when_no_sessionid_cookie(self) -> None:
        """If the login POST does not return a sessionid cookie, raise AuthenticationError."""
        respx.get(LOGIN_URL).mock(return_value=_login_get_response())
        # POST returns 200 but no sessionid cookie
        respx.post(LOGIN_URL).mock(
            return_value=httpx.Response(200, html="<html>wrong page</html>")
        )

        cfg = _make_config()
        async with AdventureLogHTTP(cfg) as http:
            auth = SessionAuth(http, cfg)
            with pytest.raises(AuthenticationError, match="sessionid"):
                await auth.login()

    @respx.mock
    async def test_login_called_only_once_when_already_authenticated(self) -> None:
        """Calling ensure_authenticated() twice should not re-POST the login form."""
        post_count = 0

        def count_post(request: httpx.Request) -> httpx.Response:
            nonlocal post_count
            post_count += 1
            return _login_post_response()

        respx.get(LOGIN_URL).mock(return_value=_login_get_response())
        respx.post(LOGIN_URL).mock(side_effect=count_post)

        cfg = _make_config()
        async with AdventureLogHTTP(cfg) as http:
            auth = SessionAuth(http, cfg)
            await auth.ensure_authenticated()
            await auth.ensure_authenticated()

        assert post_count == 1


class TestPreObtainedToken:
    async def test_pre_obtained_token_skips_login(self) -> None:
        """When session_token is set, no HTTP login requests should be made."""
        cfg = _make_config(session_token="pre-obtained-xyz")
        async with AdventureLogHTTP(cfg) as http:
            auth = SessionAuth(http, cfg)
            # No respx mock — if any HTTP call is made, it will fail with
            # a ConnectionError (no mock registered)
            await auth.ensure_authenticated()
            assert auth._authenticated

    async def test_pre_obtained_token_injected_as_sessionid(self) -> None:
        cfg = _make_config(session_token="mytoken123")
        async with AdventureLogHTTP(cfg) as http:
            auth = SessionAuth(http, cfg)
            await auth.ensure_authenticated()
            assert http.get_cookie("sessionid") == "mytoken123"


class TestConcurrentLogin:
    @respx.mock
    async def test_concurrent_ensure_authenticated_login_once(self) -> None:
        """Multiple concurrent calls to ensure_authenticated should only login once."""
        post_count = 0

        def count_post(request: httpx.Request) -> httpx.Response:
            nonlocal post_count
            post_count += 1
            return _login_post_response()

        # Allow multiple GET calls but count only POSTs
        respx.get(LOGIN_URL).mock(return_value=_login_get_response())
        respx.post(LOGIN_URL).mock(side_effect=count_post)

        cfg = _make_config()
        async with AdventureLogHTTP(cfg) as http:
            auth = SessionAuth(http, cfg)
            # Fire 5 concurrent calls
            await asyncio.gather(*[auth.ensure_authenticated() for _ in range(5)])

        assert post_count == 1


class TestLogout:
    @respx.mock
    async def test_logout_calls_delete_on_session_endpoint(self) -> None:
        """logout() should DELETE /_allauth/app/v1/auth/session."""
        logout_url = f"{BASE_URL}{LOGOUT_PATH}"
        respx.delete(logout_url).mock(return_value=httpx.Response(200))

        cfg = _make_config(session_token="tok")
        async with AdventureLogHTTP(cfg) as http:
            auth = SessionAuth(http, cfg)
            await auth.ensure_authenticated()
            await auth.logout()

        assert not auth._authenticated

    @respx.mock
    async def test_logout_clears_authenticated_flag_even_on_error(self) -> None:
        """logout() is best-effort — AuthenticationError should not propagate."""
        logout_url = f"{BASE_URL}{LOGOUT_PATH}"
        respx.delete(logout_url).mock(return_value=httpx.Response(401))

        cfg = _make_config(session_token="tok")
        async with AdventureLogHTTP(cfg) as http:
            auth = SessionAuth(http, cfg)
            await auth.ensure_authenticated()
            # Should NOT raise even though DELETE returned 401
            await auth.logout()

        assert not auth._authenticated

    @respx.mock
    async def test_logout_network_error_ignored(self) -> None:
        """logout() swallows network errors."""
        logout_url = f"{BASE_URL}{LOGOUT_PATH}"
        respx.delete(logout_url).mock(side_effect=httpx.ConnectError("gone"))

        cfg = _make_config(session_token="tok")
        async with AdventureLogHTTP(cfg) as http:
            auth = SessionAuth(http, cfg)
            await auth.ensure_authenticated()
            await auth.logout()  # must not raise

        assert not auth._authenticated
