from datetime import datetime
from io import BytesIO
from types import SimpleNamespace

import pytest
from fastapi import HTTPException, UploadFile
from minio.error import S3Error

from app.services.minio.download_service import DownloadService
from app.services.minio.minio_service import MinioService
from app.services.minio.object_service import ObjectService

from conftest import FakeBucketService, FakeObject, FakeObjectResponse


def s3_error(code: str = "NoSuchKey") -> S3Error:
    return S3Error(None, code, "message", "resource", "request-id", "host-id")


async def collect_body(response) -> bytes:
    chunks = []
    async for chunk in response.body_iterator:
        chunks.append(chunk)
    return b"".join(chunks)


@pytest.mark.anyio
async def test_simple_list_path_sorts_folders_first_and_paginates(mocker):
    minio = mocker.Mock()
    minio.list_objects.return_value = [
        FakeObject("zeta.txt", size=10),
        FakeObject("docs/", metadata={"x-amz-meta-last_modified": "2026-01-02T12:00:00"}),
        FakeObject("alpha.txt", size=5),
    ]
    service = MinioService(minio)

    result = await service.simple_list_path(path="/", user_id=7, page=1, per_page=10)

    assert result.path == "/"
    assert result.total_items == 3
    assert [item.name for item in result.items] == ["docs", "alpha.txt", "zeta.txt"]
    assert result.items[0].is_dir is True
    minio.list_objects.assert_called_once_with("user-7", prefix="", recursive=False)


@pytest.mark.anyio
async def test_simple_list_path_rejects_parent_traversal(mocker):
    service = MinioService(mocker.Mock())

    with pytest.raises(HTTPException) as exc:
        await service.simple_list_path(path="../private", user_id=1)

    assert exc.value.status_code == 400


@pytest.mark.anyio
async def test_upload_file_sanitizes_filename_and_uses_available_name(mocker):
    minio = mocker.Mock()
    minio.list_objects.return_value = [FakeObject("docs/report.txt")]
    service = DownloadService(minio, FakeBucketService())
    upload = UploadFile(
        filename="report?.txt",
        file=BytesIO(b"hello"),
        headers={"content-type": "text/plain"},
    )

    result = await service.upload_file(user_id=5, file=upload, path="/docs")

    assert result == {"name": "docs/report_.txt"}
    _, kwargs = minio.put_object.call_args
    assert kwargs["bucket_name"] == "user-5"
    assert kwargs["object_name"] == "docs/report_.txt"
    assert kwargs["length"] == 5
    assert kwargs["content_type"] == "text/plain"


@pytest.mark.anyio
async def test_preview_object_streams_with_content_type_fallback_and_closes_response(mocker):
    minio = mocker.Mock()
    minio.stat_object.return_value = SimpleNamespace(
        content_type="application/octet-stream",
        size=11,
    )
    response = FakeObjectResponse([b"hello", b" world"])
    minio.get_object.return_value = response
    service = DownloadService(minio, FakeBucketService())

    preview = await service.preview_object(user_id=5, object_name="/docs/readme.txt")
    body = await collect_body(preview)

    assert body == b"hello world"
    assert preview.media_type == "text/plain"
    assert preview.headers["content-length"] == "11"
    assert response.closed is True
    assert response.released is True


@pytest.mark.anyio
async def test_delete_file_returns_404_when_minio_key_is_missing(mocker):
    minio = mocker.Mock()
    minio.stat_object.side_effect = s3_error("NoSuchKey")
    service = ObjectService(minio, FakeBucketService())

    with pytest.raises(HTTPException) as exc:
        await service.delete_object(user_id=5, path="missing.txt")

    assert exc.value.status_code == 404
    minio.remove_object.assert_not_called()


@pytest.mark.anyio
async def test_move_rejects_same_folder_without_touching_minio(mocker):
    minio = mocker.Mock()
    service = ObjectService(minio, FakeBucketService())

    with pytest.raises(HTTPException) as exc:
        await service.move(user_id=5, source_path="docs/file.txt", destination_folder="docs")

    assert exc.value.status_code == 409
    minio.copy_object.assert_not_called()
    minio.remove_object.assert_not_called()
