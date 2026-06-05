"""Public re-exports for all AdventureLog model classes."""

from __future__ import annotations

from adventurelog.models.activity import Activity
from adventurelog.models.attachment import Attachment
from adventurelog.models.category import Category
from adventurelog.models.checklist import Checklist, ChecklistItem
from adventurelog.models.collection import (
    Collection,
    CollectionItineraryDay,
    CollectionItineraryItem,
    UltraSlimCollection,
)
from adventurelog.models.common import AdventureLogModel, PaginatedResponse
from adventurelog.models.geo import City, Country, Region, VisitedCity, VisitedRegion
from adventurelog.models.image import ContentImage
from adventurelog.models.location import Location
from adventurelog.models.lodging import Lodging
from adventurelog.models.note import Note
from adventurelog.models.trail import Trail
from adventurelog.models.transportation import Transportation
from adventurelog.models.user import (
    APIKey,
    APIKeyCreate,
    CustomUserDetails,
    ImmichIntegration,
)
from adventurelog.models.visit import Visit

__all__ = [
    # common
    "AdventureLogModel",
    "PaginatedResponse",
    # image / attachment
    "ContentImage",
    "Attachment",
    # geo
    "Country",
    "Region",
    "City",
    "VisitedCity",
    "VisitedRegion",
    # category
    "Category",
    # trail
    "Trail",
    # activity
    "Activity",
    # visit
    "Visit",
    # location
    "Location",
    # collection
    "UltraSlimCollection",
    "Collection",
    "CollectionItineraryDay",
    "CollectionItineraryItem",
    # checklist
    "Checklist",
    "ChecklistItem",
    # note
    "Note",
    # lodging
    "Lodging",
    # transportation
    "Transportation",
    # user
    "CustomUserDetails",
    "ImmichIntegration",
    "APIKey",
    "APIKeyCreate",
]
