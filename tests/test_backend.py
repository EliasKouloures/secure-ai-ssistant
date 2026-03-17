from __future__ import annotations

from core.models import ErrorCode
from services.backend import map_backend_exception


def test_timeout_error_maps_to_model_timeout() -> None:
    error = map_backend_exception(TimeoutError("timed out while waiting for response"))

    assert error.code == ErrorCode.MODEL_TIMEOUT
    assert "took too long" in error.message.lower()


def test_connection_error_maps_to_backend_unreachable() -> None:
    error = map_backend_exception(ConnectionError("connection refused"))

    assert error.code == ErrorCode.BACKEND_UNREACHABLE
    assert "could not be reached" in error.message.lower()
