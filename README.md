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

### Creating a location

```python
async with AsyncAdventureLog(...) as al:
    loc = await al.locations.create({
        "name": "Colosseum",
        "description": "Ancient amphitheatre in Rome",
        "is_visited": True,
        "latitude": 41.8902,
        "longitude": 12.4922,
    })
    print(f"Created: {loc.id}")
```

### Organising a trip with collections

```python
async with AsyncAdventureLog(...) as al:
    trip = await al.collections.create({"name": "Italy 2025", "is_archived": False})

    async for col in al.collections.list():
        print(col.name)

    shared = [c async for c in al.collections.shared()]
```

### Working with a pre-obtained token (bot use case)

```python
# Obtained and cached from a previous session:
TOKEN = "abc123sessionid"

async with AsyncAdventureLog(
    base_url="https://your-server.com",
    token=TOKEN,
) as al:
    me = await al.user.me()
```

### Recording a visit

```python
async with AsyncAdventureLog(...) as al:
    visit = await al.visits.create({
        "location": "uuid-of-location",
        "start_date": "2025-06-01",
        "end_date": "2025-06-03",
    })
```

### Geo lookups

```python
async with AsyncAdventureLog(...) as al:
    countries = await al.geo.countries()
    regions = await al.geo.regions()
    visited = await al.geo.visited_cities()
    await al.geo.create_visited_city({"city": 42})
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

All resource namespaces are available as attributes of the client after entering the context manager.

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
| `all_locations(*, page_size=100, **params)` | `AsyncIterator[Location]` | Stream via `/all/` endpoint (no visibility filters) |
| `quick_add(data)` | `Location` | Create via quick-add shortcut |
| `duplicate(id)` | `Location` | Duplicate an existing location |

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
| `archived(*, page_size=20, **params)` | `AsyncIterator[Collection]` | Stream archived collections |
| `shared(*, page_size=20, **params)` | `AsyncIterator[Collection]` | Stream collections shared with current user |
| `duplicate(id)` | `Collection` | Duplicate a collection |

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
| `api_keys()` | `list[APIKey]` | All API keys (prefix/metadata only) |
| `create_api_key(name)` | `dict` | Create API key — full key returned once |
| `delete_api_key(id)` | `None` | Revoke and delete an API key |

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
