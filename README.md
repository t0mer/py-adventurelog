# py-adventurelog

[![PyPI version](https://img.shields.io/pypi/v/py-adventurelog)](https://pypi.org/project/py-adventurelog/)
[![Python versions](https://img.shields.io/pypi/pyversions/py-adventurelog)](https://pypi.org/project/py-adventurelog/)
[![License](https://img.shields.io/github/license/t0mer/py-adventurelog)](https://github.com/t0mer/py-adventurelog/blob/main/LICENSE)

An async-first Python SDK for [AdventureLog](https://adventurelog.app/) — the self-hosted travel tracker. Built on [httpx](https://www.python-httpx.org/) and [Pydantic v2](https://docs.pydantic.dev/), fully typed, and designed as the foundation layer for Telegram/WhatsApp bots and automation scripts.

> **Unofficial project.** py-adventurelog is an independent client library. It is not affiliated with, maintained by, or endorsed by the [AdventureLog project](https://github.com/seanmorley15/AdventureLog). AdventureLog itself is licensed under the [GNU GPL v3](https://github.com/seanmorley15/AdventureLog/blob/main/LICENSE); this SDK talks to it over HTTP only and is licensed separately under Apache 2.0.

## Table of Contents

- [Features](#features)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Configuration](#configuration)
- [How It Works](#how-it-works)
- [Usage Examples](#usage-examples)
- [API Reference](#api-reference)
- [Models](#models)
- [Error Handling](#error-handling)
- [Security Notes](#security-notes)
- [Troubleshooting](#troubleshooting)
- [Known Limitations](#known-limitations)
- [Development](#development)
- [Contributing](#contributing)
- [License](#license)

## Features

- **Async-first** — every resource method is a native coroutine or async generator; the event loop is never blocked
- **Sync wrapper included** — `AdventureLog` runs the event loop internally for scripts that don't need `asyncio`
- **Typed** — Pydantic v2 models for the main resources, type hints throughout, and a `py.typed` marker for type checkers
- **Auto-pagination** — `list()` methods follow DRF `next` links transparently; you consume a single async generator
- **Stateless-friendly** — pass a pre-obtained `token` to skip the login round-trip (ideal for multi-user bots)
- **Resilient** — configurable per-request timeout and automatic retry with exponential back-off on 5xx / transport errors (idempotent methods only: `GET`, `HEAD`, `OPTIONS`, `PUT`, `DELETE`)
- **Broad API coverage** — 180 methods covering 112 AdventureLog URL paths across 21 resource namespaces
- **Typed errors** — HTTP status codes and network failures are mapped to a small exception hierarchy

## Installation

```bash
pip install py-adventurelog
```

**Requirements:** Python 3.10+ · httpx ≥ 0.27 · pydantic ≥ 2

### From source

```bash
git clone https://github.com/t0mer/py-adventurelog.git
cd py-adventurelog
pip install -e ".[dev]"
```

## Quick Start

```python
import asyncio
from adventurelog import AsyncAdventureLog

async def main():
    async with AsyncAdventureLog(
        base_url="https://your-adventurelog-server.com",
        username="you@example.com",
        password="s3cr3t",
    ) as al:
        me = await al.user.me()
        print(f"Logged in as {me.username}")

        async for location in al.locations.list(is_visited=True):
            country = location.country.name if location.country else "unknown"
            print(location.name, country)

asyncio.run(main())
```

### Synchronous usage

```python
from adventurelog import AdventureLog

with AdventureLog(
    base_url="https://your-adventurelog-server.com",
    username="you@example.com",
    password="s3cr3t",
) as al:
    locations = al.locations.list(is_visited=True)   # returns list[Location]
    print(f"You have visited {len(locations)} places")
```

> **Note:** Async generators (e.g. `locations.list()`) are fully materialised into a `list` when used through the sync wrapper. `AdventureLog` drives its own private event loop, so it cannot be used from code that is already running inside an event loop (for example a Jupyter cell or an async bot handler); use `AsyncAdventureLog` there.

## Configuration

### Constructor arguments

| Argument | Type | Default | Description |
|---|---|---|---|
| `base_url` | `str` | required | AdventureLog server root URL (the only positional argument; a trailing slash is stripped) |
| `username` | `str` | `None` | Login username — required when `token` is not provided |
| `password` | `str` | `None` | Login password — required when `token` is not provided |
| `token` | `str` | `None` | Pre-obtained `sessionid` cookie — skips login round-trip |
| `timeout` | `float` | `30.0` | Per-request timeout in seconds (passed to `httpx.AsyncClient`) |
| `max_retries` | `int` | `3` | Retries after the first attempt on 5xx / transport errors, for idempotent methods only |

All arguments except `base_url` are keyword-only. You must pass either `token` or both `username` and `password`; otherwise the constructor raises `ValueError`.

### Environment variables

The helper `ClientConfig.from_env()` reads these variables so you don't have to pass credentials in code:

| Variable | Required | Description |
|---|---|---|
| `ADVENTURELOG_BASE_URL` | yes | Server root URL |
| `ADVENTURELOG_USERNAME` | with password | Login username |
| `ADVENTURELOG_PASSWORD` | with username | Login password |
| `ADVENTURELOG_SESSION_TOKEN` | or this | Pre-obtained `sessionid` value, used instead of username + password |

Either `ADVENTURELOG_SESSION_TOKEN` or both `ADVENTURELOG_USERNAME` and `ADVENTURELOG_PASSWORD` must be set. `from_env()` raises `ValueError` otherwise. Timeout and retries are not read from the environment; pass them to the client constructor.

```python
from adventurelog.config import ClientConfig
from adventurelog import AsyncAdventureLog

config = ClientConfig.from_env()
async with AsyncAdventureLog(
    config.base_url,
    username=config.username,
    password=config.password,
    token=config.session_token,
) as al:
    ...
```

`from_env()` reads the process environment only; it does not load a `.env` file. The repository ships an [`env.example`](https://github.com/t0mer/py-adventurelog/blob/main/env.example) template. Copy it to `.env` and load it yourself (for example with `python-dotenv`, which is part of the `dev` extra). The SDK never writes to `.env`: it does not persist the session token for you.

## How It Works

### Authentication

AdventureLog uses Django session-cookie authentication. When the client enters its context (`async with` / `with`), it authenticates in one of two ways:

1. **Username + password.** The client `GET`s `/accounts/login/` to obtain the `csrftoken` cookie, then `POST`s the login form with the CSRF token. The resulting `sessionid` cookie is kept in the client's cookie jar and sent with every later request. The CSRF cookie is then discarded.
2. **Pre-obtained token.** When `token` is set, its value is injected into the cookie jar as `sessionid` and no login request is made.

Login is guarded by an `asyncio.Lock`, so concurrent calls never submit the form twice. When the context exits, the client makes a best-effort logout request (`DELETE /_allauth/app/v1/auth/session`) and ignores any error. This also happens when you passed a `token`. In practice the request does nothing: the AdventureLog backend mounts allauth under `/auth/`, not `/_allauth/`, so the server answers 404 and the SDK ignores the error. The session is not ended on the server, and a cached `token` still works after the context exits.

The SDK has no public method that returns the `sessionid` obtained by a username + password login. To reuse a session across processes, obtain the `sessionid` cookie value yourself (for example from a browser session) and pass it as `token`.

### Retries and timeouts

- Every request uses the `timeout` you set (default 30 seconds).
- `GET`, `HEAD`, `OPTIONS`, `PUT` and `DELETE` requests are retried up to `max_retries` times on HTTP 5xx responses and on `httpx` transport errors (connection failures, timeouts). The delay doubles each time, starting at 0.5 s and capped at 30 s.
- `POST` and `PATCH` requests are never retried, so a create is never sent twice.
- The login requests are sent once, without retries.
- TLS certificate verification is always on, and redirects are followed.

### Pagination

The streaming methods on `locations` and `collections` (`list()`, `all_locations()`, `archived()`, `invites()`, …) are async generators. They request the first page with your `page_size` and filters, then follow the DRF `next` URL until it is empty. `page()` fetches one page and returns a `PaginatedResponse` with `count`, `next`, `previous` and `results`. Resources without pagination (activities, visits, notes, …) return a plain `list`.

### Logging

The SDK logs through the standard `logging` module under the `adventurelog` logger namespace, at `DEBUG` level (retries, login progress, ignored logout errors). Credentials and tokens are not logged.

```python
import logging
logging.getLogger("adventurelog").setLevel(logging.DEBUG)
```

## Usage Examples

### Listing visited locations with pagination

```python
async with AsyncAdventureLog(...) as al:
    async for loc in al.locations.list(is_visited=True, page_size=50):
        print(f"{loc.name} — {loc.location}")
```

### Fetching a single page

```python
async with AsyncAdventureLog(...) as al:
    page = await al.locations.page(page=2, page_size=20)
    print(f"Page 2 of {page.count} locations")
    for loc in page.results:
        print(loc.name)
```

### Creating and sharing a collection

```python
async with AsyncAdventureLog(...) as al:
    trip = await al.collections.create({"name": "Italy 2025"})

    # Share with another user (by their user UUID)
    await al.collections.share(trip.id, "user-uuid-here")

    # Accept a pending invite to someone else's collection
    await al.collections.accept_invite("collection-uuid")
```

### Reverse-geocoding and place search

```python
async with AsyncAdventureLog(...) as al:
    place = await al.reverse_geocode.reverse_geocode(lat=41.89, lon=12.49)
    # include_meta makes the server return a dict (see Known Limitations)
    results = await al.reverse_geocode.search(query="Colosseum Rome", include_meta="true")

    # Mark regions and cities as visited, based on your visited locations
    await al.reverse_geocode.mark_visited_region()
```

### Descriptions, recommendations and calendar export

The keyword arguments are sent to the server as query parameters. The parameter names below come from the AdventureLog server, not from the SDK.

```python
async with AsyncAdventureLog(...) as al:
    # Wikipedia description and images for a place name
    desc = await al.generate.description(name="Colosseum")
    img  = await al.generate.image(name="Colosseum")

    # Nearby places (by coordinates, or by a place name the server geocodes)
    recs = await al.generate.recommendations(lat=41.89, lon=12.49)

    # Download ICS calendar
    ics_bytes = await al.generate.ics_calendar()
    with open("adventures.ics", "wb") as f:
        f.write(ics_bytes)
```

### Integrations (Immich, Strava, Wanderer)

```python
async with AsyncAdventureLog(...) as al:
    # Immich — browse albums and search photos
    albums = await al.integrations.immich_albums()
    results = await al.integrations.immich_search(query="Paris")

    # Strava — import fitness activities
    auth = await al.integrations.strava_authorize()   # dict, typically with an authorization URL
    activities = await al.integrations.strava_activities()

    # Wanderer — sync trails
    await al.integrations.wanderer_refresh()
    trails = await al.integrations.wanderer_trails()
```

### Backup export and import

```python
async with AsyncAdventureLog(...) as al:
    data = await al.backup.export()
    with open("backup.zip", "wb") as f:
        f.write(data)
```

> **Known limitation:** `backup.import_backup(data)` sends `data` as a JSON body, but current AdventureLog servers expect a multipart upload (a `file` field plus `confirm=yes`). Restoring a backup through the SDK is therefore not expected to work yet.

### Global search and stats

```python
async with AsyncAdventureLog(...) as al:
    results = await al.search.search(query="Tokyo")
    tag_types = await al.search.tag_types()
    counts = await al.stats.counts("myusername")
    print(f"Visited {counts['visited_location_count']} locations")
```

### Managing API keys

```python
async with AsyncAdventureLog(...) as al:
    new_key = await al.user.create_api_key("my-bot")
    print(new_key["key"])   # shown once only — store it now

    keys = await al.user.api_keys()
    await al.user.delete_api_key(keys[0].id)
```

## API Reference

All 21 resource namespaces are available as attributes on the client after entering the context manager. Methods that take `**params` forward them as query parameters (or, for `reverse_geocode.mark_visited_region`, as a JSON body). Methods typed `dict` or `list[dict]` return the server's raw JSON.

---

### `al.locations` — `LocationsResource`

| Method | Returns | Description |
|---|---|---|
| `list(*, page_size=20, **params)` | `AsyncIterator[Location]` | Stream all locations, follows pagination |
| `page(*, page=1, page_size=20, **params)` | `PaginatedResponse[Location]` | Fetch a single page |
| `get(id)` | `Location` | Retrieve by UUID |
| `create(data)` | `Location` | Create a new location |
| `update(id, data)` | `Location` | Full replace |
| `partial_update(id, data)` | `Location` | Partial update |
| `delete(id)` | `None` | Delete |
| `all_locations(*, page_size=100, **params)` | `AsyncIterator[Location]` | Stream via `/all/` (no visibility filter) |
| `quick_add(data)` | `Location` | Create via quick-add shortcut |
| `duplicate(id)` | `Location` | Duplicate an existing location |
| `calendar(*, page_size=20, **params)` | `AsyncIterator[Location]` | Stream calendar view |
| `filtered(*, page_size=20, **params)` | `AsyncIterator[Location]` | Stream filtered locations |
| `pins(*, page_size=20, **params)` | `AsyncIterator[Location]` | Stream map-pin locations |
| `additional_info(id)` | `dict` | Retrieve extra metadata for a location |

---

### `al.collections` — `CollectionsResource`

| Method | Returns | Description |
|---|---|---|
| `list(*, page_size=20, **params)` | `AsyncIterator[Collection]` | Stream all collections |
| `page(*, page=1, page_size=20, **params)` | `PaginatedResponse[Collection]` | Fetch a single page |
| `get(id)` | `Collection` | Retrieve by UUID |
| `create(data)` | `Collection` | Create a new collection |
| `update(id, data)` | `Collection` | Full replace |
| `partial_update(id, data)` | `Collection` | Partial update |
| `delete(id)` | `None` | Delete |
| `all_collections(*, page_size=20, **params)` | `AsyncIterator[Collection]` | Stream via `/all/` |
| `archived(*, page_size=20, **params)` | `AsyncIterator[Collection]` | Stream archived collections |
| `shared(*, page_size=20, **params)` | `AsyncIterator[Collection]` | Stream collections shared with current user |
| `duplicate(id)` | `Collection` | Duplicate a collection |
| `import_collection(data)` | `Collection` | Import a collection (sends form data; see [Known Limitations](#known-limitations)) |
| `invites(*, page_size=20, **params)` | `AsyncIterator[Collection]` | Stream pending invites (parsed as `Collection`; `.id` is the invite UUID, see [Known Limitations](#known-limitations)) |
| `can_share(id)` | `dict` | Sharing status of other users for this collection (see [Troubleshooting](#troubleshooting)) |
| `export(id)` | `bytes` | Download export file |
| `share(id, user_uuid)` | `dict` | Share with a user |
| `unshare(id, user_uuid)` | `dict` | Remove sharing with a user |
| `revoke_invite(id, invite_uuid)` | `dict` | Revoke a pending invite; the second argument is the **invited user's UUID** |
| `accept_invite(id)` | `dict` | Accept an invite |
| `decline_invite(id)` | `dict` | Decline an invite |
| `leave(id)` | `dict` | Leave a shared collection |

---

### `al.activities` — `ActivitiesResource`

| Method | Returns | Description |
|---|---|---|
| `list()` | `list[Activity]` | All activities for current user |
| `get(id)` | `Activity` | Retrieve by UUID |
| `create(data)` | `Activity` | Create a new activity |
| `update(id, data)` | `Activity` | Full replace |
| `partial_update(id, data)` | `Activity` | Partial update |
| `delete(id)` | `None` | Delete |

---

### `al.visits` — `VisitsResource`

| Method | Returns | Description |
|---|---|---|
| `list()` | `list[Visit]` | All visits for current user |
| `get(id)` | `Visit` | Retrieve by UUID |
| `create(data)` | `Visit` | Record a new visit |
| `update(id, data)` | `Visit` | Full replace |
| `partial_update(id, data)` | `Visit` | Partial update |
| `delete(id)` | `None` | Delete |

---

### `al.notes` — `NotesResource`

| Method | Returns | Description |
|---|---|---|
| `list()` | `list[Note]` | Notes for current user's collections |
| `all_notes()` | `list[Note]` | All notes including shared collections |
| `get(id)` | `Note` | Retrieve by UUID |
| `create(data)` | `Note` | Create a new note |
| `update(id, data)` | `Note` | Full replace |
| `partial_update(id, data)` | `Note` | Partial update |
| `delete(id)` | `None` | Delete |

---

### `al.checklists` — `ChecklistsResource`

| Method | Returns | Description |
|---|---|---|
| `list()` | `list[Checklist]` | All checklists for current user |
| `get(id)` | `Checklist` | Retrieve by UUID |
| `create(data)` | `Checklist` | Create a new checklist |
| `update(id, data)` | `Checklist` | Full replace |
| `partial_update(id, data)` | `Checklist` | Partial update |
| `delete(id)` | `None` | Delete |

---

### `al.lodging` — `LodgingResource`

| Method | Returns | Description |
|---|---|---|
| `list()` | `list[Lodging]` | All lodging records for current user |
| `get(id)` | `Lodging` | Retrieve by UUID |
| `create(data)` | `Lodging` | Create a lodging record |
| `update(id, data)` | `Lodging` | Full replace |
| `partial_update(id, data)` | `Lodging` | Partial update |
| `delete(id)` | `None` | Delete |
| `quick_add(data)` | `Lodging` | Create via quick-add shortcut |

---

### `al.transportations` — `TransportationsResource`

| Method | Returns | Description |
|---|---|---|
| `list()` | `list[Transportation]` | All transportation records |
| `get(id)` | `Transportation` | Retrieve by UUID |
| `create(data)` | `Transportation` | Create a transportation record |
| `update(id, data)` | `Transportation` | Full replace |
| `partial_update(id, data)` | `Transportation` | Partial update |
| `delete(id)` | `None` | Delete |

---

### `al.trails` — `TrailsResource`

| Method | Returns | Description |
|---|---|---|
| `list()` | `list[Trail]` | All trails for current user |
| `get(id)` | `Trail` | Retrieve by UUID |
| `create(data)` | `Trail` | Create a trail |
| `update(id, data)` | `Trail` | Full replace |
| `partial_update(id, data)` | `Trail` | Partial update |
| `delete(id)` | `None` | Delete |

---

### `al.images` — `ImagesResource`

| Method | Returns | Description |
|---|---|---|
| `list()` | `list[ContentImage]` | All images for current user |
| `get(id)` | `ContentImage` | Retrieve by UUID |
| `create(data)` | `ContentImage` | Create an image record |
| `update(id, data)` | `ContentImage` | Full replace |
| `partial_update(id, data)` | `ContentImage` | Partial update |
| `delete(id)` | `None` | Delete |
| `fetch_from_url(data)` | `ContentImage` | Fetch and create an image from a remote URL |
| `import_from_urls(data)` | `list[ContentImage]` | Bulk-import images from a list of URLs |
| `image_delete(id)` | `dict` | Delete the file associated with an image record |
| `toggle_primary(id)` | `ContentImage` | Toggle the primary flag on an image |

---

### `al.attachments` — `AttachmentsResource`

| Method | Returns | Description |
|---|---|---|
| `list()` | `list[dict]` | All attachments for current user |
| `get(id)` | `dict` | Retrieve by UUID |
| `create(data)` | `dict` | Create a new attachment |
| `update(id, data)` | `dict` | Full replace |
| `partial_update(id, data)` | `dict` | Partial update |
| `delete(id)` | `None` | Delete |

---

### `al.categories` — `CategoriesResource`

| Method | Returns | Description |
|---|---|---|
| `list()` | `list[Category]` | All location categories |
| `get(id)` | `Category` | Retrieve by UUID |
| `create(data)` | `Category` | Create a category |
| `update(id, data)` | `Category` | Full replace |
| `partial_update(id, data)` | `Category` | Partial update |
| `delete(id)` | `None` | Delete |

---

### `al.geo` — `GeoResource`

| Method | Returns | Description |
|---|---|---|
| `countries()` | `list[Country]` | All countries |
| `country(id)` | `Country` | Retrieve country by integer ID |
| `regions()` | `list[Region]` | All regions (states/provinces) |
| `region(id)` | `Region` | Retrieve a region by ID (a string such as a region code; the SDK's `int` type hint is wrong) |
| `visited_cities()` | `list[VisitedCity]` | Cities marked as visited |
| `create_visited_city(data)` | `VisitedCity` | Mark a city as visited |
| `delete_visited_city(id)` | `None` | Remove a visited-city record |
| `visited_regions()` | `list[VisitedRegion]` | Regions marked as visited |
| `create_visited_region(data)` | `VisitedRegion` | Mark a region as visited |
| `delete_visited_region(id)` | `None` | Remove a visited-region record |
| `check_point_in_region(**params)` | `dict` | Check whether a point (`lat`, `lon`) falls in a region |
| `region_check_all_adventures(data)` | `dict` | Check all adventures against region boundaries |
| `cities_in_region(region_id)` | `list[dict]` | All cities within a region (`region_id` is a string; the `int` hint is wrong) |
| `city_visits_in_region(region_id)` | `list[dict]` | Visited cities within a region (`region_id` is a string; the `int` hint is wrong) |
| `regions_by_country(country_code)` | `list[dict]` | Regions for a country code |
| `visits_by_country(country_code)` | `list[dict]` | Visits for a country code |

---

### `al.itineraries` — `ItinerariesResource`

#### Itinerary items (`/api/itineraries/`)

| Method | Returns | Description |
|---|---|---|
| `list_items()` | `list[CollectionItineraryItem]` | All itinerary items |
| `get_item(id)` | `CollectionItineraryItem` | Retrieve by UUID |
| `create_item(data)` | `CollectionItineraryItem` | Create an itinerary item |
| `update_item(id, data)` | `CollectionItineraryItem` | Full replace |
| `partial_update_item(id, data)` | `CollectionItineraryItem` | Partial update |
| `delete_item(id)` | `None` | Delete |
| `auto_generate(data)` | `dict` | Auto-generate an itinerary for a collection |
| `reorder(data)` | `dict` | Reorder itinerary items |

#### Itinerary days (`/api/itinerary-days/`)

| Method | Returns | Description |
|---|---|---|
| `list_days()` | `list[CollectionItineraryDay]` | All itinerary days |
| `get_day(id)` | `CollectionItineraryDay` | Retrieve by UUID |
| `create_day(data)` | `CollectionItineraryDay` | Create an itinerary day |
| `update_day(id, data)` | `CollectionItineraryDay` | Full replace |
| `partial_update_day(id, data)` | `CollectionItineraryDay` | Partial update |
| `delete_day(id)` | `None` | Delete |

---

### `al.user` — `UserResource`

| Method | Returns | Description |
|---|---|---|
| `me()` | `CustomUserDetails` | Current authenticated user profile |
| `update_profile(data)` | `CustomUserDetails` | Partially update user profile |
| `get_user(username)` | `CustomUserDetails` | Retrieve a user's public profile by username |
| `users()` | `list[CustomUserDetails]` | All users (admin) |
| `api_keys()` | `list[APIKey]` | All API keys (prefix/metadata only) |
| `create_api_key(name)` | `dict` | Create API key — full key returned once |
| `delete_api_key(id)` | `None` | Revoke and delete an API key |
| `is_registration_disabled()` | `dict` | Check whether public registration is disabled |
| `social_providers()` | `list[dict]` | Configured social auth providers |
| `disable_password()` | `dict` | Disable password login for current user |
| `enable_password()` | `None` | Re-enable password login |
| `mobile_qr()` | `dict` | Get the mobile QR login code |
| `create_mobile_qr()` | `dict` | Generate a new mobile QR login code |
| `delete_mobile_qr()` | `None` | Delete the mobile QR login code |

---

### `al.reverse_geocode` — `ReverseGeocodeResource`

| Method | Returns | Description |
|---|---|---|
| `reverse_geocode(**params)` | `dict` | Reverse-geocode coordinates (`lat`, `lon`) to a place |
| `place_details(**params)` | `dict` | Detailed information about a place (`place_id`) |
| `search(**params)` | `dict` | Search for places (`query`; pass `include_meta="true"`, see [Known Limitations](#known-limitations)) |
| `mark_visited_region(**params)` | `dict` | Mark regions and cities of your visited locations as visited |

---

### `al.integrations` — `IntegrationsResource`

#### General

| Method | Returns | Description |
|---|---|---|
| `list()` | `list[dict]` | All configured integrations |

#### Immich (self-hosted photo management)

| Method | Returns | Description |
|---|---|---|
| `immich_list()` | `list[dict]` | All Immich integration configs |
| `immich_create(data)` | `dict` | Create an Immich integration |
| `immich_get(id)` | `dict` | Retrieve by UUID |
| `immich_update(id, data)` | `dict` | Full replace |
| `immich_partial_update(id, data)` | `dict` | Partial update |
| `immich_delete(id)` | `None` | Delete |
| `immich_albums()` | `list[dict]` | All albums from Immich |
| `immich_album(album_id)` | `dict` | Retrieve a single album |
| `immich_search(**params)` | `dict` | Search Immich assets |
| `immich_get_image(integration_id, image_id)` | `dict` | Retrieve a specific Immich image |

#### Strava (fitness activity tracking)

| Method | Returns | Description |
|---|---|---|
| `strava_activities()` | `list[dict]` | Imported Strava activities |
| `strava_activity(activity_id)` | `dict` | Retrieve a single Strava activity |
| `strava_authorize()` | `dict` | Initiate OAuth authorization flow |
| `strava_callback(**params)` | `dict` | Handle OAuth callback |
| `strava_disable()` | `dict` | Disconnect Strava |

#### Wanderer (trail/route tracking)

| Method | Returns | Description |
|---|---|---|
| `wanderer_create(data)` | `dict` | Create / connect Wanderer integration |
| `wanderer_update(id, data)` | `dict` | Update Wanderer config |
| `wanderer_trails()` | `list[dict]` | Trails imported from Wanderer |
| `wanderer_refresh()` | `dict` | Re-sync trails from Wanderer |
| `wanderer_disable()` | `dict` | Disconnect Wanderer |

---

### `al.generate` — `GenerateResource`

| Method | Returns | Description |
|---|---|---|
| `description(**params)` | `dict` | Wikipedia description for a place (`name`, optional `lang`) |
| `image(**params)` | `dict` | Wikipedia images for a place (`name`, optional `lang`) |
| `ics_calendar(**params)` | `bytes` | ICS calendar export |
| `globespin(**params)` | `dict` | Globe-spin data for 3-D visualisation |
| `recommendations(**params)` | `dict` | Nearby place recommendations (`lat` + `lon` or `location`; optional `radius`, `category`) |

---

### `al.backup` — `BackupResource`

| Method | Returns | Description |
|---|---|---|
| `export()` | `bytes` | Download full data backup |
| `import_backup(data)` | `dict` | Restore data from a backup (sends JSON; see the limitation above) |

---

### `al.search` — `SearchResource`

| Method | Returns | Description |
|---|---|---|
| `search(**params)` | `dict` | Full-text search across all content (`query`) |
| `tag_types()` | `list[dict]` | Available tag type values |

---

### `al.stats` — `StatsResource`

| Method | Returns | Description |
|---|---|---|
| `counts(username)` | `dict` | Adventure count statistics for a user (e.g. `visited_location_count`, `visited_country_count`) |

---

## Models

Responses are parsed into Pydantic v2 models. Import them from `adventurelog.models`:

```python
from adventurelog.models import Location, Collection, PaginatedResponse
```

| Area | Models |
|---|---|
| Common | `AdventureLogModel` (base class), `PaginatedResponse[T]` |
| Locations | `Location`, `Visit`, `Category`, `Trail`, `Activity` |
| Collections | `Collection`, `UltraSlimCollection`, `CollectionItineraryItem`, `CollectionItineraryDay` |
| Planning | `Checklist`, `ChecklistItem`, `Note`, `Lodging`, `Transportation` |
| Media | `ContentImage`, `Attachment` |
| Geography | `Country`, `Region`, `City`, `VisitedCity`, `VisitedRegion` |
| User | `CustomUserDetails`, `APIKey`, `APIKeyCreate`, `ImmichIntegration` |

Resource model fields are optional (`PaginatedResponse` and `APIKeyCreate` have required fields), and unknown fields in a response are ignored, so the models tolerate small differences between AdventureLog versions. Decimal values such as `latitude`, `longitude`, `rating` and `price` are kept as strings, as the server sends them. Nested objects are typed, for example `Location.country` is a `Country` and `Location.visits` is a `list[Visit]`.

## Error Handling

All SDK errors inherit from `AdventureLogError`. HTTP error responses and `httpx` transport errors (connection failures, timeouts) from API calls are converted to the exceptions below.

```python
from adventurelog import (
    AsyncAdventureLog,
    AdventureLogError,
    AuthenticationError,
    NotFoundError,
    ValidationError,
    PermissionDenied,
    RateLimitError,
    ServerError,
    APIConnectionError,
)

async with AsyncAdventureLog(...) as al:
    try:
        loc = await al.locations.get("non-existent-id")
    except NotFoundError:
        print("Location not found")
    except ValidationError as e:
        print("Validation failed:", e.field_errors)
    except AuthenticationError:
        print("Login failed or session expired")
    except RateLimitError:
        print("Too many requests — back off and retry")
    except ServerError:
        print("Server returned 5xx")
    except APIConnectionError:
        print("Network or timeout error")
    except AdventureLogError as e:
        print("Unexpected SDK error:", e)
```

### Exception hierarchy

```
AdventureLogError
├── AuthenticationError     # HTTP 401 — login failed or session expired
├── PermissionDenied        # HTTP 403 — insufficient permissions
├── NotFoundError           # HTTP 404 — resource does not exist
├── ValidationError         # HTTP 400/422 and any other unmapped 4xx — carries .field_errors dict
├── RateLimitError          # HTTP 429 — server rate limit hit
├── ServerError             # HTTP 5xx — server-side failure (after retries)
└── APIConnectionError      # Network / timeout error (wraps httpx)
```

A few errors fall outside this hierarchy or behave differently:

- Network errors during login raise `AuthenticationError`, not `APIConnectionError`.
- A missing CSRF token on the login page, or a login that returns no `sessionid` cookie (for example wrong credentials), raises `AuthenticationError`.
- Missing credentials raise `ValueError` when the client (or `ClientConfig`) is constructed.
- A response that cannot be parsed as JSON, or that does not match a model, raises the underlying `ValueError` / `pydantic.ValidationError`. Note that `pydantic.ValidationError` is a different class from `adventurelog.ValidationError`.

## Security Notes

- **Keep credentials out of code.** Read them from the environment (`ClientConfig.from_env()`) or a secret store. `env.example` is a template; your real `.env` should never be committed (the repository's `.gitignore` excludes it).
- **Treat the session token like a password.** A `sessionid` value gives full access to the account until the session expires or is logged out. Store any cached token with the same care as the password, and do not log it.
- **Secrets are hidden from `repr`.** `ClientConfig` excludes `password` and `session_token` from its `repr()`, so printing a config does not leak them.
- **Use HTTPS.** Credentials are sent in the login form and the session cookie on every request. TLS certificate verification is always enabled and cannot be turned off in the SDK, so point `base_url` at an `https://` URL with a valid certificate.
- **Scope bots per user.** For multi-user bots, create one client per user with that user's own token rather than sharing one account.

## Troubleshooting

**`AuthenticationError: Failed to obtain CSRF token from the login page`**
The client could not get a `csrftoken` cookie from `<base_url>/accounts/login/`. Check that `base_url` points to the AdventureLog **backend** (the server that serves `/accounts/login/` and `/api/`), with no path suffix.

**`AuthenticationError: Login succeeded in HTTP terms but no 'sessionid' cookie was returned`**
The login form was submitted but no session was created. This usually means wrong credentials, or an account that cannot log in with a password (for example social login only, or password login disabled).

**`RuntimeError: Cannot run the event loop while another loop is running`**
You used the synchronous `AdventureLog` wrapper inside an async context. Use `AsyncAdventureLog` instead.

**`collections.can_share()` returns an odd `dict` or raises `ValueError`**
Current AdventureLog servers answer this endpoint with a list of users (each with a `status` of `available`, `pending` or `shared`), while the SDK converts the response to a `dict`. Until this is fixed, avoid relying on `can_share()`. `share()` does not depend on it.

## Known Limitations

Checked against AdventureLog `main` as of September 2026:

- **`reverse_geocode.search()`** returns a list from the server unless `include_meta` is set. The SDK converts the response with `dict(...)`, which then raises or returns garbage. Pass `include_meta="true"` so the server returns a dict.
- **`backup.import_backup(data)`** sends JSON, but the server expects a multipart upload (a `file` field plus `confirm=yes`). Restoring a backup through the SDK does not work yet.
- **`collections.import_collection(data)`** sends URL-encoded form data, but the server expects a multipart ZIP upload in a `file` field. Importing a collection through the SDK does not work yet.
- **`collections.invites()`** yields invite records parsed as `Collection`. The model's `.id` is the invite UUID, and the collection id is dropped. `accept_invite()` and `decline_invite()` need the **collection** id, so you cannot pass the `.id` from `invites()` to them.
- **`collections.can_share()`**: see [Troubleshooting](#troubleshooting).
- **Region ids** are strings (for example region codes), but `geo.region()`, `geo.cities_in_region()` and `geo.city_visits_in_region()` are type-hinted as `int`. Pass the string id; the hint is wrong.
- **Logout on exit** does nothing (see [Authentication](#authentication)).

## Development

### Project layout

```
src/adventurelog/
├── __init__.py        # public exports: clients, exceptions, __version__
├── client.py          # AsyncAdventureLog and the sync AdventureLog wrapper
├── auth.py            # session-cookie login / token injection / logout
├── config.py          # ClientConfig and from_env()
├── http.py            # httpx wrapper: retries, error mapping, cookies
├── pagination.py      # DRF pagination helpers
├── exceptions.py      # exception hierarchy
├── models/            # Pydantic v2 response models
└── resources/         # one module per API namespace
tests/unit/            # offline unit tests (respx-mocked)
```

### Running the tests

```bash
pip install -e ".[dev]"

# Unit tests (offline, no credentials needed)
pytest tests/unit/
```

The `pytest` configuration defines an `integration` marker for tests that need a live server and credentials from `env.example`, but the repository does not include any integration tests yet.

### Releasing

The [`Publish pypi package`](https://github.com/t0mer/py-adventurelog/blob/main/.github/workflows/publish.yml) workflow builds the sdist and wheel with Python 3.12 and uploads them to PyPI with the `PYPI_API_TOKEN` repository secret (token-based, not Trusted Publishing). It runs when a GitHub release is published, or manually through `workflow_dispatch`. The package version is the `version` field in `pyproject.toml`; bump it before publishing.

## Contributing

1. Fork the repository and create a branch from `main`
2. Install dev dependencies: `pip install -e ".[dev]"`
3. Make your changes; add or update tests in `tests/unit/`
4. Ensure all checks pass:

```bash
ruff check src/ tests/
ruff format src/ tests/
mypy --strict src/
pytest tests/unit/
```

5. Open a pull request against `main`

## License

Distributed under the [Apache License 2.0](https://github.com/t0mer/py-adventurelog/blob/main/LICENSE).

## Author

**Tomer Klein**
- Email: [tomer.klein@gmail.com](mailto:tomer.klein@gmail.com)
- GitHub: [@t0mer](https://github.com/t0mer)

---

*py-adventurelog is an independent open-source project and is not affiliated with or endorsed by the [AdventureLog](https://github.com/seanmorley15/AdventureLog) project.*
