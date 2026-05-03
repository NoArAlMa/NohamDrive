from datetime import timedelta
from types import SimpleNamespace

import pytest
from fastapi import HTTPException
from starlette.requests import Request

from core.security import JWTService


def make_request(*, headers: dict[str, str] | None = None, cookies: dict[str, str] | None = None):
    request = Request(
        {
            "type": "http",
            "method": "GET",
            "path": "/",
            "headers": [
                (key.lower().encode(), value.encode())
                for key, value in (headers or {}).items()
            ],
        }
    )
    request._cookies = cookies or {}
    return request


def test_jwt_roundtrip_contains_required_claims():
    service = JWTService(connection_manager=SimpleNamespace())

    token = service.create_access_token(
        {"sub": "user@example.com", "user_id": 42},
        expires_delta=timedelta(minutes=5),
        scope=["storage:read"],
    )
    payload = service.verify_token(token.token)

    assert payload["sub"] == "user@example.com"
    assert payload["user_id"] == 42
    assert payload["scope"] == ["storage:read"]
    assert "exp" in payload
    assert "jti" in payload


def test_get_token_from_request_prefers_cookie_then_bearer_header():
    service = JWTService(connection_manager=SimpleNamespace())

    assert (
        service.get_token_from_request(
            make_request(
                headers={"Authorization": "Bearer header-token"},
                cookies={"access_token": "cookie-token"},
            )
        )
        == "cookie-token"
    )
    assert (
        service.get_token_from_request(
            make_request(headers={"Authorization": "Bearer header-token"})
        )
        == "header-token"
    )


def test_get_token_from_request_rejects_missing_token():
    service = JWTService(connection_manager=SimpleNamespace())

    with pytest.raises(HTTPException) as exc:
        service.get_token_from_request(make_request())

    assert exc.value.status_code == 401


def test_verify_token_rejects_invalid_token():
    service = JWTService(connection_manager=SimpleNamespace())

    with pytest.raises(HTTPException) as exc:
        service.verify_token("not-a-valid-token")

    assert exc.value.status_code == 401
