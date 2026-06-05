"""Tests for ClientConfig."""

from __future__ import annotations

import os
from unittest.mock import patch

import pytest

from adventurelog.config import ClientConfig


BASE_URL = "https://test.example.com"


class TestClientConfigCreation:
    def test_username_password_config(self) -> None:
        cfg = ClientConfig(base_url=BASE_URL, username="alice", password="secret")
        assert cfg.username == "alice"
        assert cfg.base_url == BASE_URL

    def test_session_token_config(self) -> None:
        cfg = ClientConfig(base_url=BASE_URL, session_token="tok123")
        assert cfg.session_token == "tok123"

    def test_trailing_slash_stripped(self) -> None:
        cfg = ClientConfig(base_url="https://example.com/", session_token="t")
        assert cfg.base_url == "https://example.com"

    def test_raises_when_no_credentials(self) -> None:
        with pytest.raises(ValueError, match="session_token"):
            ClientConfig(base_url=BASE_URL)

    def test_raises_when_username_only(self) -> None:
        with pytest.raises(ValueError):
            ClientConfig(base_url=BASE_URL, username="alice")

    def test_raises_when_password_only(self) -> None:
        with pytest.raises(ValueError):
            ClientConfig(base_url=BASE_URL, password="secret")

    def test_raises_when_base_url_missing(self) -> None:
        env: dict[str, str] = {
            "ADVENTURELOG_BASE_URL": "",
            "ADVENTURELOG_SESSION_TOKEN": "tok",
        }
        with patch.dict(os.environ, env, clear=False):
            # Unset the var explicitly so it is empty
            os.environ.pop("ADVENTURELOG_BASE_URL", None)
            with pytest.raises(ValueError, match="ADVENTURELOG_BASE_URL"):
                ClientConfig.from_env()


class TestClientConfigFromEnv:
    def test_from_env_username_password(self) -> None:
        env = {
            "ADVENTURELOG_BASE_URL": BASE_URL,
            "ADVENTURELOG_USERNAME": "bob",
            "ADVENTURELOG_PASSWORD": "pass123",
        }
        with patch.dict(os.environ, env, clear=True):
            cfg = ClientConfig.from_env()
        assert cfg.base_url == BASE_URL
        assert cfg.username == "bob"
        assert cfg.password == "pass123"
        assert cfg.session_token is None

    def test_from_env_session_token(self) -> None:
        env = {
            "ADVENTURELOG_BASE_URL": BASE_URL,
            "ADVENTURELOG_SESSION_TOKEN": "mytoken",
        }
        with patch.dict(os.environ, env, clear=True):
            cfg = ClientConfig.from_env()
        assert cfg.session_token == "mytoken"
        assert cfg.username is None

    def test_from_env_missing_base_url_raises(self) -> None:
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValueError, match="ADVENTURELOG_BASE_URL"):
                ClientConfig.from_env()


class TestClientConfigRepr:
    def test_password_not_in_repr(self) -> None:
        cfg = ClientConfig(base_url=BASE_URL, username="alice", password="supersecret")
        assert "supersecret" not in repr(cfg)

    def test_session_token_not_in_repr(self) -> None:
        cfg = ClientConfig(base_url=BASE_URL, session_token="verysecrettoken")
        assert "verysecrettoken" not in repr(cfg)

    def test_username_in_repr(self) -> None:
        cfg = ClientConfig(base_url=BASE_URL, username="alice", password="secret")
        assert "alice" in repr(cfg)
