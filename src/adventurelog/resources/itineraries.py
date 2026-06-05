"""ItinerariesResource — wraps /api/itineraries/ and /api/itinerary-days/ endpoints."""

from __future__ import annotations

from typing import Any

from adventurelog.models.collection import (
    CollectionItineraryDay,
    CollectionItineraryItem,
)
from adventurelog.resources.base import BaseResource

# Short aliases used only for type annotations in this module.
_Item = CollectionItineraryItem
_Day = CollectionItineraryDay


class ItinerariesResource(BaseResource):
    """Resource for collection itinerary endpoints.

    Covers two related endpoint groups:

    - ``/api/itineraries/`` — CollectionItineraryItem records (a
      location/transportation/etc. scheduled within an itinerary).
    - ``/api/itinerary-days/`` — CollectionItineraryDay records (a
      calendar day within an itinerary).

    Both endpoint groups return plain JSON arrays (non-paginated).
    """

    # ------------------------------------------------------------------
    # Itinerary items  (/api/itineraries/)
    # ------------------------------------------------------------------

    async def list_items(self) -> list[_Item]:
        """Return all itinerary items for the current user.

        Returns:
            List of CollectionItineraryItem instances.
        """
        resp = await self._http.get("/api/itineraries/")
        return [_Item.model_validate(item) for item in resp.json()]

    async def get_item(self, id: str) -> _Item:
        """Retrieve a single itinerary item by ID.

        Args:
            id: The itinerary item's UUID.

        Returns:
            The matching CollectionItineraryItem.
        """
        resp = await self._http.get(f"/api/itineraries/{id}/")
        return _Item.model_validate(resp.json())

    async def create_item(self, data: dict[str, Any]) -> _Item:
        """Create a new itinerary item.

        Args:
            data: Itinerary item field data.

        Returns:
            The newly created CollectionItineraryItem.
        """
        resp = await self._http.post("/api/itineraries/", json=data)
        return _Item.model_validate(resp.json())

    async def update_item(self, id: str, data: dict[str, Any]) -> _Item:
        """Replace an itinerary item (full update).

        Args:
            id: The itinerary item's UUID.
            data: Complete field data.

        Returns:
            The updated CollectionItineraryItem.
        """
        resp = await self._http.put(f"/api/itineraries/{id}/", json=data)
        return _Item.model_validate(resp.json())

    async def partial_update_item(
        self, id: str, data: dict[str, Any]
    ) -> _Item:
        """Partially update an itinerary item.

        Args:
            id: The itinerary item's UUID.
            data: Fields to update.

        Returns:
            The updated CollectionItineraryItem.
        """
        resp = await self._http.patch(f"/api/itineraries/{id}/", json=data)
        return _Item.model_validate(resp.json())

    async def delete_item(self, id: str) -> None:
        """Delete an itinerary item.

        Args:
            id: The itinerary item's UUID.
        """
        await self._http.delete(f"/api/itineraries/{id}/")

    # ------------------------------------------------------------------
    # Itinerary days  (/api/itinerary-days/)
    # ------------------------------------------------------------------

    async def list_days(self) -> list[_Day]:
        """Return all itinerary days for the current user.

        Returns:
            List of CollectionItineraryDay instances.
        """
        resp = await self._http.get("/api/itinerary-days/")
        return [_Day.model_validate(item) for item in resp.json()]

    async def get_day(self, id: str) -> _Day:
        """Retrieve a single itinerary day by ID.

        Args:
            id: The itinerary day's UUID.

        Returns:
            The matching CollectionItineraryDay.
        """
        resp = await self._http.get(f"/api/itinerary-days/{id}/")
        return _Day.model_validate(resp.json())

    async def create_day(self, data: dict[str, Any]) -> _Day:
        """Create a new itinerary day.

        Args:
            data: Itinerary day field data.

        Returns:
            The newly created CollectionItineraryDay.
        """
        resp = await self._http.post("/api/itinerary-days/", json=data)
        return _Day.model_validate(resp.json())

    async def update_day(self, id: str, data: dict[str, Any]) -> _Day:
        """Replace an itinerary day (full update).

        Args:
            id: The itinerary day's UUID.
            data: Complete field data.

        Returns:
            The updated CollectionItineraryDay.
        """
        resp = await self._http.put(f"/api/itinerary-days/{id}/", json=data)
        return _Day.model_validate(resp.json())

    async def partial_update_day(
        self, id: str, data: dict[str, Any]
    ) -> _Day:
        """Partially update an itinerary day.

        Args:
            id: The itinerary day's UUID.
            data: Fields to update.

        Returns:
            The updated CollectionItineraryDay.
        """
        resp = await self._http.patch(f"/api/itinerary-days/{id}/", json=data)
        return _Day.model_validate(resp.json())

    async def delete_day(self, id: str) -> None:
        """Delete an itinerary day.

        Args:
            id: The itinerary day's UUID.
        """
        await self._http.delete(f"/api/itinerary-days/{id}/")
