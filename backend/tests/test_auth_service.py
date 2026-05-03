from datetime import datetime
from types import SimpleNamespace

import pytest
from fastapi import HTTPException

from app.schemas.auth import UserLogin
from app.services.auth_service import AuthService
from app.schemas.user import CompleteUser


class FakeBucketService:
    def __init__(self, ensure_bucket_result="user-1"):
        self.ensure_bucket_result = ensure_bucket_result

    async def ensure_bucket_exists(self, user_id: int):
        return self.ensure_bucket_result

    async def create_user_bucket(self, user_id: int):
        return f"user-{user_id}"


class FakeMinioService:
    def __init__(self, ensure_bucket_result="user-1"):
        self.bucket_service = FakeBucketService(ensure_bucket_result)


@pytest.mark.anyio
async def test_login_rejects_unknown_email(mocker):
    mocker.patch("app.services.auth_service.get_user_through_email", return_value=None)
    service = AuthService(SimpleNamespace(), FakeMinioService())

    with pytest.raises(HTTPException) as exc:
        await service.auth_login_user(
            UserLogin(email="missing@example.com", password="Password1!")
        )

    assert exc.value.status_code == 422


@pytest.mark.anyio
async def test_login_raises_when_user_bucket_cannot_be_ensured(mocker):
    user = CompleteUser(
        id=10,
        username="alex",
        full_name="Alex",
        email="alex@example.com",
        creation_date=datetime(2026, 1, 1),
        password="hashed",
    )
    mocker.patch("app.services.auth_service.get_user_through_email", return_value=user)
    service = AuthService(SimpleNamespace(), FakeMinioService(ensure_bucket_result=False))
    mocker.patch.object(service, "verify_password", return_value=True)

    with pytest.raises(HTTPException) as exc:
        await service.auth_login_user(
            UserLogin(email="alex@example.com", password="Password1!")
        )

    assert exc.value.status_code == 404
    assert "Bucket" in exc.value.detail


@pytest.mark.anyio
async def test_login_rejects_bad_password(mocker):
    user = CompleteUser(
        id=10,
        username="alex",
        full_name="Alex",
        email="alex@example.com",
        creation_date=datetime(2026, 1, 1),
        password="hashed",
    )
    mocker.patch("app.services.auth_service.get_user_through_email", return_value=user)
    service = AuthService(SimpleNamespace(), FakeMinioService())
    mocker.patch.object(service, "verify_password", return_value=False)

    with pytest.raises(HTTPException) as exc:
        await service.auth_login_user(
            UserLogin(email="alex@example.com", password="WrongPassword1!")
        )

    assert exc.value.status_code == 422
