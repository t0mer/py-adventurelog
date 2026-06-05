"""Tests for AdventureLogHTTP: error mapping, retries, connection errors."""

from __future__ import annotations

import pytest
import respx
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
from adventurelog.http import AdventureLogHTTP

BASE_URL = "https://test.example.com"


@pytest.fixture
def config() -> ClientConfig:
    return ClientConfig(base_url=BASE_URL, username="u", password="p")


@pytest.fixture
async def http(config: ClientConfig) -> AdventureLogHTTP:  # type: ignore[misc]
    async with AdventureLogHTTP(config) as client:
        yield client  # type: ignore[misc]


class TestErrorMapping:
    @respx.mock
    async def test_400_raises_validation_error(self, http: AdventureLogHTTP) -> None:
        body = {"field": ["This field is required."]}
        respx.get(f"{BASE_URL}/api/test/").mock(
            return_value=httpx.Response(400, json=body)
        )
        with pytest.raises(ValidationError) as exc_info:
            await http.get("/api/test/")
        assert exc_info.value.field_errors.get("field") == ["This field is required."]

    @respx.mock
    async def test_422_raises_validation_error(self, http: AdventureLogHTTP) -> None:
        body = {"detail": "Invalid data."}
        respx.get(f"{BASE_URL}/api/test/").mock(
            return_value=httpx.Response(422, json=body)
        )
        with pytest.raises(ValidationError):
            await http.get("/api/test/")

    @respx.mock
    async def test_401_raises_authentication_error(self, http: AdventureLogHTTP) -> None:
        respx.get(f"{BASE_URL}/api/test/").mock(
            return_value=httpx.Response(401, json={"detail": "Authentication required."})
        )
        with pytest.raises(AuthenticationError):
            await http.get("/api/test/")

    @respx.mock
    async def test_403_raises_permission_denied(self, http: AdventureLogHTTP) -> None:
        respx.get(f"{BASE_URL}/api/test/").mock(
            return_value=httpx.Response(403, json={"detail": "Forbidden."})
        )
        with pytest.raises(PermissionDenied):
            await http.get("/api/test/")

    @respx.mock
    async def test_404_raises_not_found(self, http: AdventureLogHTTP) -> None:
        respx.get(f"{BASE_URL}/api/test/").mock(
            return_value=httpx.Response(404, json={"detail": "Not found."})
        )
        with pytest.raises(NotFoundError):
            await http.get("/api/test/")

    @respx.mock
    async def test_429_raises_rate_limit_error(self, http: AdventureLogHTTP) -> None:
        respx.get(f"{BASE_URL}/api/test/").mock(
            return_value=httpx.Response(429, json={"detail": "Too many requests."})
        )
        with pytest.raises(RateLimitError):
            await http.get("/api/test/")

    @respx.mock
    async def test_500_raises_server_error(self, http: AdventureLogHTTP) -> None:
        # Need enough retries exhausted; use max_retries=0 config for simplicity
        cfg = ClientConfig(base_url=BASE_URL, username="u", password="p", max_retries=0)
        async with AdventureLogHTTP(cfg) as client:
            respx.get(f"{BASE_URL}/api/test/").mock(
                return_value=httpx.Response(500, json={"detail": "Server blew up."})
            )
            with pytest.raises(ServerError):
                await client.get("/api/test/")

    @respx.mock
    async def test_network_error_raises_api_connection_error(
        self, http: AdventureLogHTTP
    ) -> None:
        respx.get(f"{BASE_URL}/api/test/").mock(side_effect=httpx.ConnectError("refused"))
        with pytest.raises(APIConnectionError):
            # Use a config with no retries so the test is fast
            cfg = ClientConfig(base_url=BASE_URL, username="u", password="p", max_retries=0)
            async with AdventureLogHTTP(cfg) as client:
                await client.get("/api/test/")


class TestRetryBehavior:
    @respx.mock
    async def test_get_retries_on_500(self) -> None:
        """GET on 5xx should retry up to max_retries times."""
        # max_retries=2 → 3 total attempts (0 + 2 retries)
        cfg = ClientConfig(base_url=BASE_URL, username="u", password="p", max_retries=2)
        call_count = 0

        def side_effect(request: httpx.Request) -> httpx.Response:
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                return httpx.Response(500, json={"detail": "oops"})
            return httpx.Response(200, json={"ok": True})

        respx.get(f"{BASE_URL}/api/test/").mock(side_effect=side_effect)

        async with AdventureLogHTTP(cfg) as client:
            # Patch sleep to avoid actual waiting
            import adventurelog.http as http_mod
            original_sleep = __import__("asyncio").sleep

            async def fast_sleep(_: float) -> None:
                pass

            import asyncio
            asyncio.sleep = fast_sleep  # type: ignore[assignment]
            try:
                resp = await client.get("/api/test/")
            finally:
                asyncio.sleep = original_sleep  # type: ignore[assignment]

        assert call_count == 3
        assert resp.json() == {"ok": True}

    @respx.mock
    async def test_post_does_not_retry_on_500(self) -> None:
        """POST on 5xx should NOT retry."""
        cfg = ClientConfig(base_url=BASE_URL, username="u", password="p", max_retries=3)
        call_count = 0

        def side_effect(request: httpx.Request) -> httpx.Response:
            nonlocal call_count
            call_count += 1
            return httpx.Response(500, json={"detail": "oops"})

        respx.post(f"{BASE_URL}/api/test/").mock(side_effect=side_effect)

        async with AdventureLogHTTP(cfg) as client:
            with pytest.raises(ServerError):
                await client.post("/api/test/", json={})

        assert call_count == 1

    @respx.mock
    async def test_get_raises_after_exhausting_retries(self) -> None:
        """GET that never succeeds raises ServerError after retries are exhausted."""
        cfg = ClientConfig(base_url=BASE_URL, username="u", password="p", max_retries=1)

        respx.get(f"{BASE_URL}/api/test/").mock(
            return_value=httpx.Response(503, json={"detail": "service unavailable"})
        )

        import asyncio

        original_sleep = asyncio.sleep

        async def fast_sleep(_: float) -> None:
            pass

        asyncio.sleep = fast_sleep  # type: ignore[assignment]
        try:
            async with AdventureLogHTTP(cfg) as client:
                with pytest.raises(ServerError):
                    await client.get("/api/test/")
        finally:
            asyncio.sleep = original_sleep  # type: ignore[assignment]


class TestSuccessfulResponse:
    @respx.mock
    async def test_successful_get_returns_response(self, http: AdventureLogHTTP) -> None:
        payload = {"id": "abc", "name": "Test Location"}
        respx.get(f"{BASE_URL}/api/locations/abc/").mock(
            return_value=httpx.Response(200, json=payload)
        )
        resp = await http.get("/api/locations/abc/")
        assert resp.json() == payload
        assert resp.status_code == 200

    @respx.mock
    async def test_successful_post_returns_response(self, http: AdventureLogHTTP) -> None:
        payload = {"id": "new-id", "name": "New Location"}
        respx.post(f"{BASE_URL}/api/locations/").mock(
            return_value=httpx.Response(201, json=payload)
        )
        resp = await http.post("/api/locations/", json={"name": "New Location"})
        assert resp.json()["id"] == "new-id"

    @respx.mock
    async def test_delete_returns_204(self, http: AdventureLogHTTP) -> None:
        respx.delete(f"{BASE_URL}/api/locations/abc/").mock(
            return_value=httpx.Response(204)
        )
        resp = await http.delete("/api/locations/abc/")
        assert resp.status_code == 204


class TestValidationErrorFieldErrors:
    @respx.mock
    async def test_field_errors_populated_from_body(
        self, http: AdventureLogHTTP
    ) -> None:
        body = {
            "username": ["This field is required."],
            "email": ["Enter a valid email address.", "This field is too long."],
        }
        respx.post(f"{BASE_URL}/api/users/").mock(
            return_value=httpx.Response(400, json=body)
        )
        with pytest.raises(ValidationError) as exc_info:
            await http.post("/api/users/", json={})
        err = exc_info.value
        assert err.field_errors["username"] == ["This field is required."]
        assert "Enter a valid email address." in err.field_errors["email"]

    @respx.mock
    async def test_non_json_error_body(self, http: AdventureLogHTTP) -> None:
        respx.get(f"{BASE_URL}/api/test/").mock(
            return_value=httpx.Response(404, content=b"Not Found", headers={"content-type": "text/plain"})
        )
        with pytest.raises(NotFoundError):
            await http.get("/api/test/")
