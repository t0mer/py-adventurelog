"""Tests for AsyncAdventureLog context manager and resource wiring."""

from __future__ import annotations

import httpx
import pytest
import respx

from adventurelog.client import AsyncAdventureLog
from adventurelog.resources.activities import ActivitiesResource
from adventurelog.resources.categories import CategoriesResource
from adventurelog.resources.checklists import ChecklistsResource
from adventurelog.resources.collections import CollectionsResource
from adventurelog.resources.geo import GeoResource
from adventurelog.resources.images import ImagesResource
from adventurelog.resources.itineraries import ItinerariesResource
from adventurelog.resources.locations import LocationsResource
from adventurelog.resources.lodging import LodgingResource
from adventurelog.resources.notes import NotesResource
from adventurelog.resources.trails import TrailsResource
from adventurelog.resources.transportations import TransportationsResource
from adventurelog.resources.user import UserResource
from adventurelog.resources.visits import VisitsResource

BASE_URL = "https://test.example.com"
LOGIN_URL = f"{BASE_URL}/accounts/login/"
LOGOUT_URL = f"{BASE_URL}/_allauth/app/v1/auth/session"


def _mock_login(mock: respx.MockRouter) -> None:
    """Register the two login mocks (GET + POST) on the given mock router.

    We use 200 for the POST response (rather than 302) to avoid httpx following
    the redirect to '/', which would require an extra mock.  The auth code checks
    the cookie jar, not the status code, so 200 is correct for testing.
    """
    mock.get(LOGIN_URL).mock(
        return_value=httpx.Response(
            200,
            html="<form></form>",
            headers={"Set-Cookie": "csrftoken=csrf123; Path=/"},
        )
    )
    mock.post(LOGIN_URL).mock(
        return_value=httpx.Response(
            200,
            html="<html>OK</html>",
            headers={"Set-Cookie": "sessionid=session456; Path=/"},
        )
    )


def _mock_logout(mock: respx.MockRouter) -> None:
    mock.delete(LOGOUT_URL).mock(return_value=httpx.Response(200))


class TestAsyncAdventureLogContextManager:
    @respx.mock
    async def test_login_called_on_aenter(self) -> None:
        """__aenter__ should trigger the login flow when using username+password."""
        post_count = 0

        def count_post(request: httpx.Request) -> httpx.Response:
            nonlocal post_count
            post_count += 1
            return httpx.Response(
                200,
                html="<html>OK</html>",
                headers={"Set-Cookie": "sessionid=session456; Path=/"},
            )

        respx.get(LOGIN_URL).mock(
            return_value=httpx.Response(
                200,
                html="<form></form>",
                headers={"Set-Cookie": "csrftoken=csrf123; Path=/"},
            )
        )
        respx.post(LOGIN_URL).mock(side_effect=count_post)
        respx.delete(LOGOUT_URL).mock(return_value=httpx.Response(200))

        async with AsyncAdventureLog(
            BASE_URL, username="u", password="p"
        ):
            pass

        assert post_count == 1

    @respx.mock
    async def test_all_resource_namespaces_exist_after_aenter(self) -> None:
        """All 14 resource namespaces must be available inside the context."""
        _mock_login(respx)
        _mock_logout(respx)

        async with AsyncAdventureLog(BASE_URL, username="u", password="p") as al:
            assert isinstance(al.locations, LocationsResource)
            assert isinstance(al.collections, CollectionsResource)
            assert isinstance(al.activities, ActivitiesResource)
            assert isinstance(al.transportations, TransportationsResource)
            assert isinstance(al.notes, NotesResource)
            assert isinstance(al.checklists, ChecklistsResource)
            assert isinstance(al.lodging, LodgingResource)
            assert isinstance(al.trails, TrailsResource)
            assert isinstance(al.images, ImagesResource)
            assert isinstance(al.categories, CategoriesResource)
            assert isinstance(al.geo, GeoResource)
            assert isinstance(al.visits, VisitsResource)
            assert isinstance(al.itineraries, ItinerariesResource)
            assert isinstance(al.user, UserResource)

    @respx.mock
    async def test_pre_obtained_token_skips_login(self) -> None:
        """With token= provided, no login POST should be made."""
        post_count = 0

        def fail_if_called(request: httpx.Request) -> httpx.Response:
            nonlocal post_count
            post_count += 1
            return httpx.Response(200)

        # Register GET and POST — if POST is called, we count it
        respx.get(LOGIN_URL).mock(side_effect=fail_if_called)
        respx.post(LOGIN_URL).mock(side_effect=fail_if_called)
        respx.delete(LOGOUT_URL).mock(return_value=httpx.Response(200))

        async with AsyncAdventureLog(BASE_URL, token="pretoken123"):
            pass

        assert post_count == 0

    @respx.mock
    async def test_logout_called_on_aexit(self) -> None:
        """__aexit__ should call logout best-effort."""
        logout_count = 0

        def count_logout(request: httpx.Request) -> httpx.Response:
            nonlocal logout_count
            logout_count += 1
            return httpx.Response(200)

        _mock_login(respx)
        respx.delete(LOGOUT_URL).mock(side_effect=count_logout)

        async with AsyncAdventureLog(BASE_URL, username="u", password="p"):
            pass

        assert logout_count == 1

    @respx.mock
    async def test_exception_in_body_propagates(self) -> None:
        """An exception raised inside the context block propagates correctly."""
        _mock_login(respx)
        respx.delete(LOGOUT_URL).mock(return_value=httpx.Response(200))

        with pytest.raises(RuntimeError, match="test error"):
            async with AsyncAdventureLog(BASE_URL, username="u", password="p"):
                raise RuntimeError("test error")

    @respx.mock
    async def test_aexit_called_even_when_body_raises(self) -> None:
        """__aexit__ (and therefore logout) is called even when body raises."""
        logout_count = 0

        def count_logout(request: httpx.Request) -> httpx.Response:
            nonlocal logout_count
            logout_count += 1
            return httpx.Response(200)

        _mock_login(respx)
        respx.delete(LOGOUT_URL).mock(side_effect=count_logout)

        with pytest.raises(ValueError):
            async with AsyncAdventureLog(BASE_URL, username="u", password="p"):
                raise ValueError("boom")

        assert logout_count == 1

    @respx.mock
    async def test_logout_failure_does_not_mask_original_exception(self) -> None:
        """If logout itself fails, the original exception from the body still propagates."""
        _mock_login(respx)
        # Logout will get a 500 which raises ServerError internally,
        # but SessionAuth.logout() catches all exceptions.
        respx.delete(LOGOUT_URL).mock(return_value=httpx.Response(500))

        with pytest.raises(KeyError, match="original"):
            async with AsyncAdventureLog(BASE_URL, username="u", password="p"):
                raise KeyError("original")
