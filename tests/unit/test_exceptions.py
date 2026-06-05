"""Tests for the AdventureLog exception hierarchy."""

from __future__ import annotations

import pytest

from adventurelog.exceptions import (
    APIConnectionError,
    AdventureLogError,
    AuthenticationError,
    NotFoundError,
    PermissionDenied,
    RateLimitError,
    ServerError,
    ValidationError,
)


class TestExceptionHierarchy:
    """All concrete exceptions must be subclasses of AdventureLogError."""

    def test_authentication_error_is_base(self) -> None:
        assert issubclass(AuthenticationError, AdventureLogError)

    def test_permission_denied_is_base(self) -> None:
        assert issubclass(PermissionDenied, AdventureLogError)

    def test_not_found_error_is_base(self) -> None:
        assert issubclass(NotFoundError, AdventureLogError)

    def test_validation_error_is_base(self) -> None:
        assert issubclass(ValidationError, AdventureLogError)

    def test_rate_limit_error_is_base(self) -> None:
        assert issubclass(RateLimitError, AdventureLogError)

    def test_server_error_is_base(self) -> None:
        assert issubclass(ServerError, AdventureLogError)

    def test_api_connection_error_is_base(self) -> None:
        assert issubclass(APIConnectionError, AdventureLogError)


class TestExceptionMessages:
    def test_message_preserved(self) -> None:
        exc = AuthenticationError("bad credentials")
        assert str(exc) == "bad credentials"

    def test_not_found_message(self) -> None:
        exc = NotFoundError("location not found")
        assert "location not found" in str(exc)

    def test_server_error_message(self) -> None:
        exc = ServerError("internal server error")
        assert str(exc) == "internal server error"


class TestValidationError:
    def test_field_errors_default_empty(self) -> None:
        exc = ValidationError("bad input")
        assert exc.field_errors == {}

    def test_field_errors_stored(self) -> None:
        errors = {"username": ["This field is required."]}
        exc = ValidationError("bad input", field_errors=errors)
        assert exc.field_errors == errors

    def test_field_errors_multiple_fields(self) -> None:
        errors = {
            "username": ["Required."],
            "email": ["Enter a valid email.", "Too long."],
        }
        exc = ValidationError("validation failed", field_errors=errors)
        assert exc.field_errors["email"] == ["Enter a valid email.", "Too long."]

    def test_message_accessible(self) -> None:
        exc = ValidationError("something wrong", field_errors={"f": ["e"]})
        assert str(exc) == "something wrong"

    def test_can_be_caught_as_base(self) -> None:
        with pytest.raises(AdventureLogError):
            raise ValidationError("err")
