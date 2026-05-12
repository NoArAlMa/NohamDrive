from io import BytesIO
from types import SimpleNamespace

import pytest
from fastapi import UploadFile
from minio.error import S3Error

from app.services.profile_picture_service import ProfilePictureService
from conftest import FakeObjectResponse


def s3_error(code: str = "NoSuchKey") -> S3Error:
    return S3Error(None, code, "message", "resource", "request-id", "host-id")


class FakeBucketService:
    async def ensure_bucket_exists(self, user_id: int) -> str:
        return f"user-{user_id}"


@pytest.mark.anyio
async def test_get_picture_generates_and_stores_svg_when_missing(mocker):
    minio = mocker.Mock()
    minio.get_object.side_effect = s3_error("NoSuchKey")
    minio.stat_object.side_effect = s3_error("NoSuchKey")
    minio_service = SimpleNamespace(minio=minio, bucket_service=FakeBucketService())
    service = ProfilePictureService(minio_service)

    data, content_type = await service.get_picture(user_id=7, full_name="Jean Pierre")

    assert content_type.startswith("image/svg+xml")
    assert b"JP" in data
    minio.put_object.assert_called_once()


@pytest.mark.anyio
async def test_get_picture_returns_existing_object_bytes_with_content_type(mocker):
    minio = mocker.Mock()
    minio.get_object.return_value = FakeObjectResponse([b"png-bytes"])
    minio.stat_object.return_value = SimpleNamespace(content_type="image/png")
    minio_service = SimpleNamespace(minio=minio, bucket_service=FakeBucketService())
    service = ProfilePictureService(minio_service)

    data, content_type = await service.get_picture(user_id=3, full_name="Someone")

    assert data == b"png-bytes"
    assert content_type == "image/png"


@pytest.mark.anyio
async def test_set_picture_overwrites_fixed_object_name(mocker):
    minio = mocker.Mock()
    minio_service = SimpleNamespace(minio=minio, bucket_service=FakeBucketService())
    service = ProfilePictureService(minio_service)
    upload = UploadFile(
        filename="avatar.png",
        file=BytesIO(b"abc"),
        headers={"content-type": "image/png"},
    )

    result = await service.set_picture(user_id=11, file=upload)

    assert result["object_name"] == "__profile__/avatar"
    assert result["content_type"] == "image/png"
    _, kwargs = minio.put_object.call_args
    assert kwargs["bucket_name"] == "user-11"
    assert kwargs["object_name"] == "__profile__/avatar"
    assert kwargs["length"] == 3

