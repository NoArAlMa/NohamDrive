import sys
from datetime import datetime, timedelta
from pathlib import Path
from types import SimpleNamespace

import pytest


ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT_DIR))


class FakeObject(SimpleNamespace):
    def __init__(
        self,
        object_name: str,
        *,
        size: int | None = 0,
        last_modified: datetime | None = None,
        content_type: str | None = None,
        metadata: dict[str, str] | None = None,
        etag: str | None = None,
    ):
        super().__init__(
            object_name=object_name,
            size=size,
            last_modified=last_modified or datetime(2026, 1, 1, 12, 0, 0),
            content_type=content_type,
            metadata=metadata,
            etag=etag,
        )


class FakeObjectResponse:
    def __init__(self, chunks: list[bytes]):
        self._chunks = chunks
        self.closed = False
        self.released = False

    def stream(self, _chunk_size: int):
        yield from self._chunks

    def read(self, size: int | None = None):
        data = b"".join(self._chunks)
        return data if size is None else data[:size]

    def close(self):
        self.closed = True

    def release_conn(self):
        self.released = True


class FakeBucketService:
    async def get_user_bucket(self, user_id: int) -> str:
        return f"user-{user_id}"


def future_datetime() -> datetime:
    return datetime.now() + timedelta(days=1)


@pytest.fixture
def anyio_backend():
    return "asyncio"
