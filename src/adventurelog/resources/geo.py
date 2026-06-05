"""GeoResource — wraps country, region, and visited geo endpoints."""

from __future__ import annotations

from typing import Any

from adventurelog.models.geo import Country, Region, VisitedCity, VisitedRegion
from adventurelog.resources.base import BaseResource


class GeoResource(BaseResource):
    """Resource for geographic reference and visited-geography endpoints.

    Covers:
    - ``/api/countries/`` — country reference data
    - ``/api/regions/`` — region (state/province) reference data
    - ``/api/visitedcity/`` — cities the user has visited
    - ``/api/visitedregion/`` — regions the user has visited
    """

    # ------------------------------------------------------------------
    # Countries
    # ------------------------------------------------------------------

    async def countries(self) -> list[Country]:
        """Return all countries.

        Returns:
            List of :class:`~adventurelog.models.geo.Country` instances.
        """
        resp = await self._http.get("/api/countries/")
        return [Country.model_validate(item) for item in resp.json()]

    async def country(self, id: int) -> Country:
        """Retrieve a single country by ID.

        Args:
            id: The country's integer primary key.

        Returns:
            The matching :class:`~adventurelog.models.geo.Country`.
        """
        resp = await self._http.get(f"/api/countries/{id}/")
        return Country.model_validate(resp.json())

    # ------------------------------------------------------------------
    # Regions
    # ------------------------------------------------------------------

    async def regions(self) -> list[Region]:
        """Return all regions.

        Returns:
            List of :class:`~adventurelog.models.geo.Region` instances.
        """
        resp = await self._http.get("/api/regions/")
        return [Region.model_validate(item) for item in resp.json()]

    async def region(self, id: int) -> Region:
        """Retrieve a single region by ID.

        Args:
            id: The region's integer primary key.

        Returns:
            The matching :class:`~adventurelog.models.geo.Region`.
        """
        resp = await self._http.get(f"/api/regions/{id}/")
        return Region.model_validate(resp.json())

    # ------------------------------------------------------------------
    # Visited cities
    # ------------------------------------------------------------------

    async def visited_cities(self) -> list[VisitedCity]:
        """Return all cities the current user has visited.

        Returns:
            List of :class:`~adventurelog.models.geo.VisitedCity` instances.
        """
        resp = await self._http.get("/api/visitedcity/")
        return [VisitedCity.model_validate(item) for item in resp.json()]

    async def create_visited_city(self, data: dict[str, Any]) -> VisitedCity:
        """Mark a city as visited.

        Args:
            data: VisitedCity field data (must include ``city`` FK).

        Returns:
            The newly created :class:`~adventurelog.models.geo.VisitedCity`.
        """
        resp = await self._http.post("/api/visitedcity/", json=data)
        return VisitedCity.model_validate(resp.json())

    async def delete_visited_city(self, id: int) -> None:
        """Remove a visited-city record.

        Args:
            id: The visited-city record's integer primary key.
        """
        await self._http.delete(f"/api/visitedcity/{id}/")

    # ------------------------------------------------------------------
    # Visited regions
    # ------------------------------------------------------------------

    async def visited_regions(self) -> list[VisitedRegion]:
        """Return all regions the current user has visited.

        Returns:
            List of :class:`~adventurelog.models.geo.VisitedRegion` instances.
        """
        resp = await self._http.get("/api/visitedregion/")
        return [VisitedRegion.model_validate(item) for item in resp.json()]

    async def create_visited_region(self, data: dict[str, Any]) -> VisitedRegion:
        """Mark a region as visited.

        Args:
            data: VisitedRegion field data (must include ``region`` FK).

        Returns:
            The newly created :class:`~adventurelog.models.geo.VisitedRegion`.
        """
        resp = await self._http.post("/api/visitedregion/", json=data)
        return VisitedRegion.model_validate(resp.json())

    async def delete_visited_region(self, id: int) -> None:
        """Remove a visited-region record.

        Args:
            id: The visited-region record's integer primary key.
        """
        await self._http.delete(f"/api/visitedregion/{id}/")
