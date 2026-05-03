from types import SimpleNamespace

import pytest
from fastapi import HTTPException
from minio.error import S3Error

from app.utils.minio_utils import MinioUtils


def fake_objects(*names: str):
    return [SimpleNamespace(object_name=name) for name in names]


def s3_error(code: str = "NoSuchKey") -> S3Error:
    return S3Error(None, code, "message", "resource", "request-id", "host-id")


def test_sanitize_name_keeps_safe_unicode_and_replaces_forbidden_characters():
    assert MinioUtils.sanitize_name(" écouté moi.mp3 ") == "écouté moi.mp3"
    assert MinioUtils.sanitize_name("report#draft?.pdf") == "report_draft_.pdf"


@pytest.mark.parametrize("name", ["", "   ", ".", "..", "###"])
def test_sanitize_name_rejects_empty_or_unsafe_names(name: str):
    with pytest.raises(HTTPException) as exc:
        MinioUtils.sanitize_name(name)

    assert exc.value.status_code == 400


def test_normalize_path_rejects_parent_traversal_and_preserves_folder_slash():
    assert MinioUtils.normalize_path("/docs/reports", is_folder=True) == "docs/reports/"

    with pytest.raises(HTTPException) as exc:
        MinioUtils.normalize_path("../secrets.txt")

    assert exc.value.status_code == 400


def test_generate_available_name_handles_nested_conflicts_and_suffixes(mocker):
    minio = mocker.Mock()
    minio.list_objects.return_value = fake_objects(
        "folder/report.txt",
        "folder/report (1).txt",
        "folder/report (3).txt",
    )

    assert (
        MinioUtils.generate_available_name(
            minio,
            bucket_name="bucket",
            base_name="report (1).txt",
            parent_path="folder",
        )
        == "folder/report (2).txt"
    )


@pytest.mark.anyio
async def test_resolve_path_type_prefers_file_then_directory_then_not_found(mocker):
    minio = mocker.Mock()
    minio.stat_object.return_value = object()

    assert await MinioUtils.resolve_path_type(minio, "bucket", "docs/file.txt") == "file"

    minio.stat_object.side_effect = s3_error()
    minio.list_objects.return_value = fake_objects("docs/file.txt")
    assert await MinioUtils.resolve_path_type(minio, "bucket", "docs") == "dir"

    minio.list_objects.return_value = []
    assert await MinioUtils.resolve_path_type(minio, "bucket", "missing") == "not_found"
