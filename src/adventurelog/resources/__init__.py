"""Public re-exports for all AdventureLog resource classes."""

from __future__ import annotations

from adventurelog.resources.activities import ActivitiesResource
from adventurelog.resources.base import BaseResource
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

__all__ = [
    "BaseResource",
    "LocationsResource",
    "CollectionsResource",
    "ActivitiesResource",
    "TransportationsResource",
    "NotesResource",
    "ChecklistsResource",
    "LodgingResource",
    "TrailsResource",
    "ImagesResource",
    "CategoriesResource",
    "GeoResource",
    "VisitsResource",
    "ItinerariesResource",
    "UserResource",
]
