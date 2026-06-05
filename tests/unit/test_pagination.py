"""Tests for paginate() and fetch_page() helpers."""

from __future__ import annotations

import httpx
import pytest
import respx

from adventurelog.config import ClientConfig
from adventurelog.exceptions import AdventureLogError
from adventurelog.http import AdventureLogHTTP
from adventurelog.pagination import fetch_page, paginate

BASE_URL = "https://test.example.com"


@pytest.fixture
def config() -> ClientConfig:
    return ClientConfig(base_url=BASE_URL, username="u", password="p")


@pytest.fixture
async def http(config: ClientConfig) -> AdventureLogHTTP:  # type: ignore[misc]
    async with AdventureLogHTTP(config) as client:
        yield client  # type: ignore[misc]


class TestPaginate:
    @respx.mock
    async def test_single_page_yields_all_items(self, http: AdventureLogHTTP) -> None:
        payload = {
            "count": 2,
            "next": None,
            "previous": None,
            "results": [{"id": "1", "name": "A"}, {"id": "2", "name": "B"}],
        }
        respx.get(f"{BASE_URL}/api/items/").mock(return_value=httpx.Response(200, json=payload))

        items = [item async for item in paginate(http, "/api/items/")]
        assert len(items) == 2
        assert items[0]["name"] == "A"
        assert items[1]["name"] == "B"

    @respx.mock
    async def test_follows_next_link(self, http: AdventureLogHTTP) -> None:
        page1 = {
            "count": 4,
            "next": f"{BASE_URL}/api/items/?page=2",
            "previous": None,
            "results": [{"id": "1"}, {"id": "2"}],
        }
        page2 = {
            "count": 4,
            "next": None,
            "previous": f"{BASE_URL}/api/items/?page=1",
            "results": [{"id": "3"}, {"id": "4"}],
        }
        respx.get(f"{BASE_URL}/api/items/").mock(
            side_effect=lambda req: httpx.Response(
                200, json=page2 if "page=2" in str(req.url) else page1
            )
        )

        items = [item async for item in paginate(http, "/api/items/")]
        assert len(items) == 4
        assert items[2]["id"] == "3"
        assert items[3]["id"] == "4"

    @respx.mock
    async def test_stops_at_null_next(self, http: AdventureLogHTTP) -> None:
        payload = {
            "count": 1,
            "next": None,
            "previous": None,
            "results": [{"id": "only"}],
        }
        respx.get(f"{BASE_URL}/api/items/").mock(return_value=httpx.Response(200, json=payload))

        items = [item async for item in paginate(http, "/api/items/")]
        assert len(items) == 1

    @respx.mock
    async def test_plain_list_response_yielded_directly(
        self, http: AdventureLogHTTP
    ) -> None:
        """A plain list response (non-paginated) should be yielded as-is."""
        payload = [{"id": "1"}, {"id": "2"}, {"id": "3"}]
        respx.get(f"{BASE_URL}/api/items/").mock(return_value=httpx.Response(200, json=payload))

        items = [item async for item in paginate(http, "/api/items/")]
        assert len(items) == 3
        assert items[0]["id"] == "1"

    @respx.mock
    async def test_empty_results(self, http: AdventureLogHTTP) -> None:
        payload = {"count": 0, "next": None, "previous": None, "results": []}
        respx.get(f"{BASE_URL}/api/items/").mock(return_value=httpx.Response(200, json=payload))

        items = [item async for item in paginate(http, "/api/items/")]
        assert items == []

    @respx.mock
    async def test_params_sent_on_first_request_only(
        self, http: AdventureLogHTTP
    ) -> None:
        """Initial params should be sent on page 1; subsequent pages use the next URL."""
        page1 = {
            "count": 2,
            "next": f"{BASE_URL}/api/items/?page=2",
            "previous": None,
            "results": [{"id": "1"}],
        }
        page2 = {
            "count": 2,
            "next": None,
            "previous": None,
            "results": [{"id": "2"}],
        }

        captured_params: list[dict[str, str]] = []

        def capture(request: httpx.Request) -> httpx.Response:
            captured_params.append(dict(request.url.params))
            if "page=2" in str(request.url):
                return httpx.Response(200, json=page2)
            return httpx.Response(200, json=page1)

        respx.get(f"{BASE_URL}/api/items/").mock(side_effect=capture)

        items = [
            item
            async for item in paginate(http, "/api/items/", params={"page_size": "10"})
        ]
        assert len(items) == 2
        # First request should carry our params
        assert captured_params[0].get("page_size") == "10"


class TestFetchPage:
    @respx.mock
    async def test_returns_dict_with_count_and_results(
        self, http: AdventureLogHTTP
    ) -> None:
        payload = {
            "count": 5,
            "next": None,
            "previous": None,
            "results": [{"id": str(i)} for i in range(5)],
        }
        respx.get(f"{BASE_URL}/api/items/").mock(return_value=httpx.Response(200, json=payload))

        result = await fetch_page(http, "/api/items/")
        assert result["count"] == 5
        assert len(result["results"]) == 5

    @respx.mock
    async def test_page_param_forwarded(self, http: AdventureLogHTTP) -> None:
        payload = {"count": 10, "next": None, "previous": None, "results": []}
        captured: list[dict[str, str]] = []

        def capture(request: httpx.Request) -> httpx.Response:
            captured.append(dict(request.url.params))
            return httpx.Response(200, json=payload)

        respx.get(f"{BASE_URL}/api/items/").mock(side_effect=capture)

        await fetch_page(http, "/api/items/", page=3, page_size=5)
        assert captured[0]["page"] == "3"
        assert captured[0]["page_size"] == "5"

    @respx.mock
    async def test_plain_list_wrapped_in_envelope(self, http: AdventureLogHTTP) -> None:
        payload = [{"id": "a"}, {"id": "b"}]
        respx.get(f"{BASE_URL}/api/items/").mock(return_value=httpx.Response(200, json=payload))

        result = await fetch_page(http, "/api/items/")
        assert result["count"] == 2
        assert result["next"] is None
        assert result["results"] == payload

    @respx.mock
    async def test_unexpected_response_shape_raises(self, http: AdventureLogHTTP) -> None:
        """A non-dict, non-list response should raise AdventureLogError."""
        respx.get(f"{BASE_URL}/api/items/").mock(
            return_value=httpx.Response(200, json="unexpected string")
        )
        with pytest.raises(AdventureLogError):
            await fetch_page(http, "/api/items/")
