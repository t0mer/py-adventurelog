"""AsyncAdventureLog client and synchronous wrapper for the AdventureLog SDK.

Primary entry point::

    async with AsyncAdventureLog(base_url="...", username="...", password="...") as al:
        async for loc in al.locations.list():
            ...
        me = await al.user.me()

For synchronous callers::

    with AdventureLog(base_url="...", username="...", password="...") as al:
        locs = al.locations.list()   # returns list[Location]
        me = al.user.me()
"""

from __future__ import annotations

import asyncio
import inspect
import logging
from typing import Any, TypeVar

from adventurelog.auth import SessionAuth
from adventurelog.config import ClientConfig
from adventurelog.http import AdventureLogHTTP
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

logger = logging.getLogger(__name__)

_T = TypeVar("_T")


class AsyncAdventureLog:
    """Async context-manager client for the AdventureLog API.

    All resource namespaces are available after entering the context::

        async with AsyncAdventureLog(base_url=..., username=..., password=...) as al:
            me = await al.user.me()
            async for loc in al.locations.list():
                print(loc.name)

    Args:
        base_url: The AdventureLog server root URL (no trailing slash).
        username: Login username.  Required when ``token`` is not provided.
        password: Login password.  Required when ``token`` is not provided.
        token: Pre-obtained ``sessionid`` cookie value.  Skips the login
            round-trip when provided (useful for bots that cache tokens).
        timeout: Per-request timeout in seconds (default 30).
        max_retries: Maximum retry attempts for idempotent requests on
            5xx/transport errors (default 3).
    """

    # Resource namespaces — declared here so type-checkers see them even
    # before __aenter__ sets the live instances.
    locations: LocationsResource
    collections: CollectionsResource
    activities: ActivitiesResource
    transportations: TransportationsResource
    notes: NotesResource
    checklists: ChecklistsResource
    lodging: LodgingResource
    trails: TrailsResource
    images: ImagesResource
    categories: CategoriesResource
    geo: GeoResource
    visits: VisitsResource
    itineraries: ItinerariesResource
    user: UserResource

    def __init__(
        self,
        base_url: str,
        *,
        username: str | None = None,
        password: str | None = None,
        token: str | None = None,
        timeout: float = 30.0,
        max_retries: int = 3,
    ) -> None:
        self._config = ClientConfig(
            base_url=base_url,
            username=username,
            password=password,
            session_token=token,
            timeout=timeout,
            max_retries=max_retries,
        )
        self._http: AdventureLogHTTP | None = None
        self._auth: SessionAuth | None = None

    async def __aenter__(self) -> AsyncAdventureLog:
        self._http = AdventureLogHTTP(self._config)
        await self._http.__aenter__()

        self._auth = SessionAuth(self._http, self._config)
        await self._auth.ensure_authenticated()

        # Wire resource namespaces now that the authenticated HTTP client exists.
        self.locations = LocationsResource(self._http)
        self.collections = CollectionsResource(self._http)
        self.activities = ActivitiesResource(self._http)
        self.transportations = TransportationsResource(self._http)
        self.notes = NotesResource(self._http)
        self.checklists = ChecklistsResource(self._http)
        self.lodging = LodgingResource(self._http)
        self.trails = TrailsResource(self._http)
        self.images = ImagesResource(self._http)
        self.categories = CategoriesResource(self._http)
        self.geo = GeoResource(self._http)
        self.visits = VisitsResource(self._http)
        self.itineraries = ItinerariesResource(self._http)
        self.user = UserResource(self._http)

        return self

    async def __aexit__(self, *exc: Any) -> None:
        await self.logout()
        if self._http is not None:
            await self._http.__aexit__(*exc)
            self._http = None

    async def login(self) -> None:
        """Explicitly authenticate with the server.

        This is called automatically by ``__aenter__``.  Call it directly only
        when using the client without the context-manager protocol.
        """
        if self._auth is None:
            raise RuntimeError(
                "Client is not set up. Use 'async with AsyncAdventureLog(...)' "
                "or call __aenter__ first."
            )
        await self._auth.ensure_authenticated()

    async def logout(self) -> None:
        """Log out and clear the session cookie.

        Best-effort: any exception is swallowed and logged.  Called automatically
        by ``__aexit__``.
        """
        if self._auth is None:
            return
        try:
            await self._auth.logout()
        except Exception as exc:  # noqa: BLE001
            logger.debug("Logout error (ignored): %s", exc)
        finally:
            self._auth = None


# ---------------------------------------------------------------------------
# Sync wrapper
# ---------------------------------------------------------------------------


class _SyncResourceProxy:
    """Thin synchronous proxy around an async resource instance.

    Wraps every public method of the resource so that:
    - Regular coroutines are run to completion via the event loop.
    - Async generators are drained into a list and returned.

    This approach is intentionally simple — bots are async-first and the sync
    wrapper is provided only as a convenience for scripts or interactive use.
    """

    def __init__(self, resource: Any, loop: asyncio.AbstractEventLoop) -> None:
        self._resource = resource
        self._loop = loop

    def __getattr__(self, name: str) -> Any:
        attr = getattr(self._resource, name)
        if not callable(attr):
            return attr

        def wrapper(*args: Any, **kwargs: Any) -> Any:
            result = attr(*args, **kwargs)
            if inspect.isasyncgen(result):
                # Drain the async generator into a list.
                async def _drain() -> list[Any]:
                    return [item async for item in result]

                return self._loop.run_until_complete(_drain())
            if asyncio.iscoroutine(result):
                return self._loop.run_until_complete(result)
            return result

        return wrapper


class AdventureLog:
    """Synchronous context-manager client for the AdventureLog API.

    A thin wrapper around :class:`AsyncAdventureLog` that runs the event loop
    internally so callers do not need ``asyncio``.

    .. note::
        Methods that return async generators (e.g. ``locations.list()``) will
        return ``list[Model]`` here, not an iterator, because the whole sequence
        must be materialised to cross the sync boundary.

    ::

        with AdventureLog(base_url=..., username=..., password=...) as al:
            locs = al.locations.list()  # list[Location]
            me = al.user.me()

    Args:
        base_url: The AdventureLog server root URL.
        username: Login username.
        password: Login password.
        token: Pre-obtained session token (skips login).
        timeout: Per-request timeout in seconds (default 30).
        max_retries: Retry attempts for idempotent requests (default 3).
    """

    def __init__(
        self,
        base_url: str,
        *,
        username: str | None = None,
        password: str | None = None,
        token: str | None = None,
        timeout: float = 30.0,
        max_retries: int = 3,
    ) -> None:
        self._async_client = AsyncAdventureLog(
            base_url,
            username=username,
            password=password,
            token=token,
            timeout=timeout,
            max_retries=max_retries,
        )
        self._loop = asyncio.new_event_loop()

    def __enter__(self) -> AdventureLog:
        self._loop.run_until_complete(self._async_client.__aenter__())
        # Expose resource proxies that transparently run coroutines/async-gens.
        self.locations = _SyncResourceProxy(self._async_client.locations, self._loop)
        self.collections = _SyncResourceProxy(
            self._async_client.collections, self._loop
        )
        self.activities = _SyncResourceProxy(self._async_client.activities, self._loop)
        self.transportations = _SyncResourceProxy(
            self._async_client.transportations, self._loop
        )
        self.notes = _SyncResourceProxy(self._async_client.notes, self._loop)
        self.checklists = _SyncResourceProxy(self._async_client.checklists, self._loop)
        self.lodging = _SyncResourceProxy(self._async_client.lodging, self._loop)
        self.trails = _SyncResourceProxy(self._async_client.trails, self._loop)
        self.images = _SyncResourceProxy(self._async_client.images, self._loop)
        self.categories = _SyncResourceProxy(self._async_client.categories, self._loop)
        self.geo = _SyncResourceProxy(self._async_client.geo, self._loop)
        self.visits = _SyncResourceProxy(self._async_client.visits, self._loop)
        self.itineraries = _SyncResourceProxy(
            self._async_client.itineraries, self._loop
        )
        self.user = _SyncResourceProxy(self._async_client.user, self._loop)
        return self

    def __exit__(self, *exc: Any) -> None:
        try:
            self._loop.run_until_complete(self._async_client.__aexit__(*exc))
        finally:
            self._loop.close()
