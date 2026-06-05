"""Shared fixtures for py-adventurelog unit tests."""

from __future__ import annotations

import pytest

from adventurelog.config import ClientConfig
from adventurelog.http import AdventureLogHTTP

BASE_URL = "https://test.example.com"


@pytest.fixture
def config() -> ClientConfig:
    """A minimal ClientConfig with username/password credentials."""
    return ClientConfig(
        base_url=BASE_URL,
        username="testuser",
        password="testpass",
    )


@pytest.fixture
def token_config() -> ClientConfig:
    """A ClientConfig using a pre-obtained session token."""
    return ClientConfig(
        base_url=BASE_URL,
        session_token="pre-obtained-token-xyz",
    )


@pytest.fixture
async def http_client(config: ClientConfig) -> AdventureLogHTTP:  # type: ignore[misc]
    """A live AdventureLogHTTP async context manager, ready for use."""
    async with AdventureLogHTTP(config) as client:
        yield client  # type: ignore[misc]
