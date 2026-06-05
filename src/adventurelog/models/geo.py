"""Geographic reference models: Country, Region, City, VisitedCity, VisitedRegion."""

from __future__ import annotations

from pydantic import ConfigDict

from adventurelog.models.common import AdventureLogModel


class Country(AdventureLogModel):
    """A country reference object."""

    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    id: int | None = None
    flag_url: str | None = None
    num_regions: int | None = None
    num_visits: int | None = None
    name: str | None = None
    country_code: str | None = None
    subregion: str | None = None
    capital: str | None = None
    longitude: str | None = None  # DecimalField serialized as string
    latitude: str | None = None  # DecimalField serialized as string


class Region(AdventureLogModel):
    """A region (state/province) reference object."""

    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    id: int | None = None
    num_cities: int | None = None
    country_name: str | None = None
    name: str | None = None
    longitude: str | None = None  # DecimalField serialized as string
    latitude: str | None = None  # DecimalField serialized as string
    country: int | str | None = None  # FK to Country


class City(AdventureLogModel):
    """A city reference object."""

    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    id: int | None = None
    region_name: str | None = None
    country_name: str | None = None
    name: str | None = None
    longitude: str | None = None  # DecimalField serialized as string
    latitude: str | None = None  # DecimalField serialized as string
    region: int | str | None = None  # FK to Region


class VisitedCity(AdventureLogModel):
    """A city that the user has visited."""

    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    id: int | None = None
    user: int | str | None = None
    city: City | None = None
    longitude: str | None = None  # DecimalField serialized as string
    latitude: str | None = None  # DecimalField serialized as string
    name: str | None = None


class VisitedRegion(AdventureLogModel):
    """A region that the user has visited."""

    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    id: int | None = None
    user: int | str | None = None
    region: Region | None = None
    longitude: str | None = None  # DecimalField serialized as string
    latitude: str | None = None  # DecimalField serialized as string
    name: str | None = None
