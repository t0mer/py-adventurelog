# py-adventurelog

[![PyPI version](https://img.shields.io/pypi/v/py-adventurelog)](https://pypi.org/project/py-adventurelog/)
[![Python versions](https://img.shields.io/pypi/pyversions/py-adventurelog)](https://pypi.org/project/py-adventurelog/)
[![License](https://img.shields.io/pypi/l/py-adventurelog)](https://github.com/t0mer/py-adventurelog/blob/main/LICENSE)

An async-first Python SDK for [AdventureLog](https://adventurelog.app/) — the self-hosted travel tracker. Built on [httpx](https://www.python-httpx.org/) and [Pydantic v2](https://docs.pydantic.dev/), fully typed, and designed as the foundation layer for Telegram/WhatsApp bots and automation scripts.

## Features

- **Async-first** — every resource method is a native coroutine or async generator; the event loop is never blocked
- **Sync wrapper included** — `AdventureLog` runs the event loop internally for scripts that don't need `asyncio`
- **Fully typed** — Pydantic v2 models for every response; full `mypy --strict` compatibility
- **Auto-pagination** — `list()` methods follow DRF `next` links transparently; you consume a single async generator
- **Stateless-friendly** — pass a pre-obtained `token` to skip the login round-trip (ideal for multi-user bots)
- **Resilient** — configurable per-request timeout and automatic retry with exponential back-off on 5xx / transport errors
- **Full API coverage** — all 112 endpoints across 21 resource namespaces

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
            print(location.name, location.country)

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

> **Note:** Async generators (e.g. `locations.list()`) are fully materialised into a `list` when used through the sync wrapper.

## Configuration

### Constructor arguments

| Argument | Type | Default | Description |
|---|---|---|---|
| `base_url` | `str` | required | AdventureLog server root URL (no trailing slash) |
| `username` | `str` | `None` | Login username — required when `token` is not provided |
| `password` | `str` | `None` | Login password — required when `token` is not provided |
| `token` | `str` | `None` | Pre-obtained `sessionid` cookie — skips login round-trip |
| `timeout` | `float` | `30.0` | Per-request timeout in seconds |
| `max_retries` | `int` | `3` | Retry attempts on 5xx / transport errors |

### Environment variables

The helper `ClientConfig.from_env()` reads these variables so you don't have to pass credentials in code:

| Variable | Required | Description |
|---|---|---|
| `ADVENTURELOG_BASE_URL` | yes | Server root URL |
| `ADVENTURELOG_USERNAME` | one of these | Login username |
| `ADVENTURELOG_PASSWORD` | one of these | Login password |
| `ADVENTURELOG_SESSION_TOKEN` | or this | Pre-obtained session token |

```python
from adventurelog.config import ClientConfig
from adventurelog import AsyncAdventureLog

config = ClientConfig.from_env()
async with AsyncAdventureLog(
    base_url=config.base_url,
    username=config.username,
    password=config.password,
) as al:
    ...
```

## Usage Examples

### Listing visited locations with pagination

```python
async with AsyncAdventureLog(...) as al:
    async for loc in al.locations.list(is_visited=True, page_size=50):
        print(f"{loc.name} — {loc.country}")
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

    # Check sharing eligibility, then share with a user
    info = await al.collections.can_share(trip.id)
    if info.get("can_share"):
        await al.collections.share(trip.id, "user-uuid-here")

    # Accept a pending invite
    await al.collections.accept_invite("collection-uuid")
```

### Reverse-geocoding and place search

```python
async with AsyncAdventureLog(...) as al:
    place = await al.reverse_geocode.reverse_geocode(lat=41.89, lng=12.49)
    results = await al.reverse_geocode.search(query="Colosseum Rome")
    await al.reverse_geocode.mark_visited_region(lat=41.89, lng=12.49)
```

### AI generation

```python
async with AsyncAdventureLog(...) as al:
    desc = await al.generate.description(location_id="uuid-here")
    img  = await al.generate.image(location_id="uuid-here")
    recs = await al.generate.recommendations(query="beaches in Italy")

    # Download ICS calendar
    ics_bytes = await al.generate.ics_calendar()
    with open("adventures.ics", "wb") as f:
        f.write(ics_bytes)
```

### Integrations (Immich, Strava, Wanderer)

```python
async with AsyncAdventureLog(...) as al:
    # Immich — browse albums and import photos
    albums = await al.integrations.immich_albums()
    results = await al.integrations.immich_search(query="Paris")

    # Strava — import fitness activities
    auth_url = await al.integrations.strava_authorize()
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

All 21 resource namespaces are available as attributes on the client after entering the context manager.

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
| `import_collection(data)` | `Collection` | Import a collection from form data |
| `invites(*, page_size=20, **params)` | `AsyncIterator[Collection]` | Stream pending invites |
| `can_share(id)` | `dict` | Check whether the collection can be shared |
| `export(id)` | `bytes` | Download export file |
| `share(id, user_uuid)` | `dict` | Share with a user |
| `unshare(id, user_uuid)` | `dict` | Remove sharing with a user |
| `revoke_invite(id, invite_uuid)` | `dict` | Revoke a pending invite |
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
| `region(id)` | `Region` | Retrieve region by integer ID |
| `visited_cities()` | `list[VisitedCity]` | Cities marked as visited |
| `create_visited_city(data)` | `VisitedCity` | Mark a city as visited |
| `delete_visited_city(id)` | `None` | Remove a visited-city record |
| `visited_regions()` | `list[VisitedRegion]` | Regions marked as visited |
| `create_visited_region(data)` | `VisitedRegion` | Mark a region as visited |
| `delete_visited_region(id)` | `None` | Remove a visited-region record |
| `check_point_in_region(**params)` | `dict` | Check whether a lat/lng falls in a region |
| `region_check_all_adventures(data)` | `dict` | Check all adventures against region boundaries |
| `cities_in_region(region_id)` | `list[dict]` | All cities within a region |
| `city_visits_in_region(region_id)` | `list[dict]` | Visited cities within a region |
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
| `reverse_geocode(**params)` | `dict` | Reverse-geocode a lat/lng to a place name |
| `place_details(**params)` | `dict` | Retrieve detailed information about a place |
| `search(**params)` | `dict` | Search for places by name or query string |
| `mark_visited_region(**params)` | `dict` | Mark the region at a lat/lng as visited |

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
| `description(**params)` | `dict` | AI-generated description for a location |
| `image(**params)` | `dict` | AI-generated image for a location |
| `ics_calendar(**params)` | `bytes` | ICS calendar export |
| `globespin(**params)` | `dict` | Globe-spin data for 3-D visualisation |
| `recommendations(**params)` | `dict` | AI-powered location recommendations |

---

### `al.backup` — `BackupResource`

| Method | Returns | Description |
|---|---|---|
| `export()` | `bytes` | Download full data backup |
| `import_backup(data)` | `dict` | Restore data from a backup |

---

### `al.search` — `SearchResource`

| Method | Returns | Description |
|---|---|---|
| `search(**params)` | `dict` | Full-text search across all content |
| `tag_types()` | `list[dict]` | Available tag type values |

---

### `al.stats` — `StatsResource`

| Method | Returns | Description |
|---|---|---|
| `counts(username)` | `dict` | Adventure count statistics for a user |

---

## Error Handling

All SDK errors inherit from `AdventureLogError`. Raw `httpx` exceptions never escape to callers.

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
├── ValidationError         # HTTP 400/422 — carries .field_errors dict
├── RateLimitError          # HTTP 429 — server rate limit hit
├── ServerError             # HTTP 5xx — server-side failure
└── APIConnectionError      # Network / timeout error (wraps httpx)
```

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

## Running the tests

```bash
# Unit tests (offline, no credentials needed)
pytest tests/unit/

# Integration tests (require a live server)
# Copy env.example to .env and fill in your credentials
pytest tests/integration/ -m integration
```

## License

Distributed under the [Apache License 2.0](https://github.com/t0mer/py-adventurelog/blob/main/LICENSE).

## Author

**Tomer Klein**
- Email: [tomer.klein@gmail.com](mailto:tomer.klein@gmail.com)
- GitHub: [@t0mer](https://github.com/t0mer)

---

*py-adventurelog is an independent open-source project and is not affiliated with or endorsed by the AdventureLog project.*
