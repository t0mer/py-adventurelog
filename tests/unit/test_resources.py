"""Tests for LocationsResource, GeoResource, and UserResource."""

from __future__ import annotations

import httpx
import pytest
import respx

from adventurelog.config import ClientConfig
from adventurelog.http import AdventureLogHTTP
from adventurelog.models.geo import Country
from adventurelog.models.location import Location
from adventurelog.models.user import CustomUserDetails
from adventurelog.resources.geo import GeoResource
from adventurelog.resources.locations import LocationsResource
from adventurelog.resources.user import UserResource

BASE_URL = "https://test.example.com"


@pytest.fixture
def config() -> ClientConfig:
    return ClientConfig(base_url=BASE_URL, username="u", password="p")


@pytest.fixture
async def http(config: ClientConfig) -> AdventureLogHTTP:  # type: ignore[misc]
    async with AdventureLogHTTP(config) as client:
        yield client  # type: ignore[misc]


# ---------------------------------------------------------------------------
# Shared sample data
# ---------------------------------------------------------------------------

LOCATION_DATA = {
    "id": "loc-uuid-1",
    "name": "Eiffel Tower",
    "description": "A famous tower.",
    "is_visited": True,
    "tags": ["paris", "landmark"],
    "is_public": True,
}

COUNTRY_DATA = {
    "id": 1,
    "name": "France",
    "country_code": "FR",
    "subregion": "Western Europe",
}

USER_DATA = {
    "pk": 42,
    "username": "testuser",
    "email": "testuser@example.com",
    "first_name": "Test",
    "last_name": "User",
}


# ---------------------------------------------------------------------------
# LocationsResource
# ---------------------------------------------------------------------------


class TestLocationsGet:
    @respx.mock
    async def test_get_returns_location(self, http: AdventureLogHTTP) -> None:
        respx.get(f"{BASE_URL}/api/locations/loc-uuid-1/").mock(
            return_value=httpx.Response(200, json=LOCATION_DATA)
        )
        resource = LocationsResource(http)
        loc = await resource.get("loc-uuid-1")
        assert isinstance(loc, Location)
        assert loc.id == "loc-uuid-1"
        assert loc.name == "Eiffel Tower"

    @respx.mock
    async def test_get_unknown_id_propagates_not_found(
        self, http: AdventureLogHTTP
    ) -> None:
        from adventurelog.exceptions import NotFoundError

        respx.get(f"{BASE_URL}/api/locations/nonexistent/").mock(
            return_value=httpx.Response(404, json={"detail": "Not found."})
        )
        resource = LocationsResource(http)
        with pytest.raises(NotFoundError):
            await resource.get("nonexistent")


class TestLocationsCreate:
    @respx.mock
    async def test_create_returns_location(self, http: AdventureLogHTTP) -> None:
        respx.post(f"{BASE_URL}/api/locations/").mock(
            return_value=httpx.Response(201, json=LOCATION_DATA)
        )
        resource = LocationsResource(http)
        loc = await resource.create({"name": "Eiffel Tower"})
        assert isinstance(loc, Location)
        assert loc.name == "Eiffel Tower"

    @respx.mock
    async def test_create_sends_json_body(self, http: AdventureLogHTTP) -> None:
        captured: list[bytes] = []

        def capture(request: httpx.Request) -> httpx.Response:
            captured.append(request.content)
            return httpx.Response(201, json=LOCATION_DATA)

        respx.post(f"{BASE_URL}/api/locations/").mock(side_effect=capture)
        resource = LocationsResource(http)
        await resource.create({"name": "Eiffel Tower", "tags": ["paris"]})
        import json

        body = json.loads(captured[0])
        assert body["name"] == "Eiffel Tower"
        assert "paris" in body["tags"]


class TestLocationsDelete:
    @respx.mock
    async def test_delete_returns_none(self, http: AdventureLogHTTP) -> None:
        respx.delete(f"{BASE_URL}/api/locations/loc-uuid-1/").mock(
            return_value=httpx.Response(204)
        )
        resource = LocationsResource(http)
        result = await resource.delete("loc-uuid-1")
        assert result is None


class TestLocationsList:
    @respx.mock
    async def test_list_yields_locations(self, http: AdventureLogHTTP) -> None:
        payload = {
            "count": 2,
            "next": None,
            "previous": None,
            "results": [
                {**LOCATION_DATA, "id": "1", "name": "Place A"},
                {**LOCATION_DATA, "id": "2", "name": "Place B"},
            ],
        }
        respx.get(f"{BASE_URL}/api/locations/").mock(
            return_value=httpx.Response(200, json=payload)
        )
        resource = LocationsResource(http)
        locations = [loc async for loc in resource.list()]
        assert len(locations) == 2
        assert all(isinstance(loc, Location) for loc in locations)
        assert locations[0].name == "Place A"
        assert locations[1].name == "Place B"

    @respx.mock
    async def test_list_follows_pagination(self, http: AdventureLogHTTP) -> None:
        page1 = {
            "count": 3,
            "next": f"{BASE_URL}/api/locations/?page=2&page_size=2",
            "previous": None,
            "results": [
                {**LOCATION_DATA, "id": "1", "name": "A"},
                {**LOCATION_DATA, "id": "2", "name": "B"},
            ],
        }
        page2 = {
            "count": 3,
            "next": None,
            "previous": None,
            "results": [
                {**LOCATION_DATA, "id": "3", "name": "C"},
            ],
        }
        respx.get(f"{BASE_URL}/api/locations/").mock(
            side_effect=lambda req: httpx.Response(
                200, json=page2 if "page=2" in str(req.url) else page1
            )
        )
        resource = LocationsResource(http)
        locations = [loc async for loc in resource.list(page_size=2)]
        assert len(locations) == 3

    @respx.mock
    async def test_list_empty_returns_no_items(self, http: AdventureLogHTTP) -> None:
        payload = {"count": 0, "next": None, "previous": None, "results": []}
        respx.get(f"{BASE_URL}/api/locations/").mock(
            return_value=httpx.Response(200, json=payload)
        )
        resource = LocationsResource(http)
        locations = [loc async for loc in resource.list()]
        assert locations == []


class TestLocationsQuickAdd:
    @respx.mock
    async def test_quick_add_calls_correct_endpoint(
        self, http: AdventureLogHTTP
    ) -> None:
        respx.post(f"{BASE_URL}/api/locations/quick-add/").mock(
            return_value=httpx.Response(201, json=LOCATION_DATA)
        )
        resource = LocationsResource(http)
        loc = await resource.quick_add({"name": "Quick Place"})
        assert isinstance(loc, Location)


# ---------------------------------------------------------------------------
# GeoResource
# ---------------------------------------------------------------------------


class TestGeoCountries:
    @respx.mock
    async def test_countries_returns_list_of_country(
        self, http: AdventureLogHTTP
    ) -> None:
        payload = [COUNTRY_DATA, {**COUNTRY_DATA, "id": 2, "name": "Germany", "country_code": "DE"}]
        respx.get(f"{BASE_URL}/api/countries/").mock(
            return_value=httpx.Response(200, json=payload)
        )
        resource = GeoResource(http)
        countries = await resource.countries()
        assert len(countries) == 2
        assert all(isinstance(c, Country) for c in countries)
        assert countries[0].name == "France"

    @respx.mock
    async def test_country_by_id(self, http: AdventureLogHTTP) -> None:
        respx.get(f"{BASE_URL}/api/countries/1/").mock(
            return_value=httpx.Response(200, json=COUNTRY_DATA)
        )
        resource = GeoResource(http)
        country = await resource.country(1)
        assert isinstance(country, Country)
        assert country.id == 1
        assert country.country_code == "FR"


# ---------------------------------------------------------------------------
# UserResource
# ---------------------------------------------------------------------------


class TestUserMe:
    @respx.mock
    async def test_me_returns_custom_user_details(self, http: AdventureLogHTTP) -> None:
        respx.get(f"{BASE_URL}/auth/user-metadata/").mock(
            return_value=httpx.Response(200, json=USER_DATA)
        )
        resource = UserResource(http)
        user = await resource.me()
        assert isinstance(user, CustomUserDetails)
        assert user.pk == 42
        assert user.username == "testuser"
        assert user.email == "testuser@example.com"

    @respx.mock
    async def test_me_calls_correct_path(self, http: AdventureLogHTTP) -> None:
        captured_paths: list[str] = []

        def capture(request: httpx.Request) -> httpx.Response:
            captured_paths.append(str(request.url.path))
            return httpx.Response(200, json=USER_DATA)

        respx.get(f"{BASE_URL}/auth/user-metadata/").mock(side_effect=capture)
        resource = UserResource(http)
        await resource.me()
        assert "/auth/user-metadata/" in captured_paths
