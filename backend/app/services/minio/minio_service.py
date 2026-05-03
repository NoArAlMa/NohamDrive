import datetime
import threading
import time
from fastapi import HTTPException, Query, Request
from fastapi.concurrency import run_in_threadpool
from minio import Minio
from minio.error import S3Error

from app.schemas.file_tree import (
    SimpleFileItem,
    SimpleFileTreeResponse,
    FullFileItem,
    FullFileTreeResponse,
)
from app.services.minio.bucket_service import BucketService
from app.services.minio.object_service import ObjectService
from app.services.minio.download_service import DownloadService
from core.logging import setup_logger


# Initialisation du logger
logger = setup_logger(__name__)


class MinioService:
    # Cache intentionally small + short-lived: it targets "UI refresh storms" (same prefix
    # requested repeatedly within a few seconds), and avoids holding large directory
    # listings in memory for too long.
    _CACHE_TTL_S = 5.0
    _CACHE_MAX_KEYS = 256
    _CACHE_MAX_ITEMS = 2000

    def __init__(self, minio: Minio):
        self.minio: Minio = minio
        self.bucket_service = BucketService(minio)
        self.object_service = ObjectService(minio, self.bucket_service)
        self.download_service = DownloadService(minio, self.bucket_service)

        self._cache_lock = threading.Lock()
        # key -> (expires_at_monotonic, items)
        self._simple_list_cache: dict[tuple[str, str], tuple[float, list[SimpleFileItem]]] = {}
        self._full_list_cache: dict[tuple[str, str, bool], tuple[float, list[FullFileItem]]] = {}

    def _cache_get(self, cache: dict, key):
        now = time.monotonic()
        with self._cache_lock:
            entry = cache.get(key)
            if not entry:
                return None
            expires_at, payload = entry
            if expires_at <= now:
                cache.pop(key, None)
                return None
            return payload

    def _cache_set(self, cache: dict, key, payload):
        # Basic size control to avoid unbounded growth.
        now = time.monotonic()
        expires_at = now + self._CACHE_TTL_S
        with self._cache_lock:
            if len(cache) >= self._CACHE_MAX_KEYS:
                # Drop one arbitrary key; TTL is short, so a simple eviction is fine.
                cache.pop(next(iter(cache)), None)
            cache[key] = (expires_at, payload)

    async def simple_list_path(
        self,
        path: str = "",
        user_id: int = 1,
        page: int = Query(1, gt=0),
        per_page: int = Query(30, gt=0, le=100),
    ) -> SimpleFileTreeResponse:
        try:
            bucket_name = await self.bucket_service.get_user_bucket(user_id=user_id)
            normalized_path = path.strip("/")
            if normalized_path:
                normalized_path += "/"

            if ".." in normalized_path.split("/"):
                raise HTTPException(status_code=400, detail="Invalid path")

            start = (page - 1) * per_page
            end = start + per_page

            cache_key = (bucket_name, normalized_path)
            cached = self._cache_get(self._simple_list_cache, cache_key)
            if cached is None:
                def list_objects_all() -> list[SimpleFileItem]:
                    items: list[SimpleFileItem] = []
                    for obj in self.minio.list_objects(
                        bucket_name,
                        prefix=normalized_path,
                        recursive=False,
                    ):
                        if obj.object_name == normalized_path:
                            continue
                        if not obj.object_name:
                            continue

                        name = obj.object_name.removeprefix(normalized_path).rstrip("/")
                        is_dir = obj.object_name.endswith("/")

                        last_modified = obj.last_modified if obj.last_modified else None
                        if is_dir and obj.metadata:
                            lm = obj.metadata.get("x-amz-meta-last_modified")
                            if lm:
                                last_modified = datetime.datetime.fromisoformat(lm)

                        items.append(
                            SimpleFileItem(
                                name=name,
                                size=None if is_dir else obj.size,
                                is_dir=is_dir,
                                last_modified=last_modified,
                            )
                        )

                    # Deterministic ordering for pagination and UI consistency.
                    items.sort(key=lambda x: (not x.is_dir, (x.name or "").lower()))
                    return items

                all_items = await run_in_threadpool(list_objects_all)
                if len(all_items) <= self._CACHE_MAX_ITEMS:
                    self._cache_set(self._simple_list_cache, cache_key, all_items)
            else:
                all_items = cached

            total_items = len(all_items)
            objects = all_items[start:end]

            total_pages = (total_items + per_page - 1) // per_page

            return SimpleFileTreeResponse(
                path="/" + normalized_path if normalized_path else "/",
                items=objects,
                total_pages=total_pages,
                total_items=total_items,
                per_page=per_page,
                page=page,
            )

        except S3Error as e:
            logger.error(f"Échec de la liste du chemin {path} : {e}")
            raise HTTPException(
                status_code=404 if e.code == "NoSuchKey" else 500,
                detail="Impossible de lister le chemin",
            )

    async def full_list_path(
        self,
        path: str = "",
        user_id: int = 1,
        recursive: bool = True,
    ) -> FullFileTreeResponse:
        """
        Liste TOUS les objets dans un bucket Minio, avec métadonnées complètes.
        Args:
            path: Chemin relatif (ex: "dossier/").
            user_id: ID de l'utilisateur.
            recursive: Si True, liste aussi les sous-dossiers.
        Returns:
            FullFileTreeResponse: Arborescence complète avec hashs, tailles, etc.
        """
        try:
            bucket_name = await self.bucket_service.get_user_bucket(user_id=user_id)
            normalized_path = path.strip("/")
            if normalized_path:
                normalized_path += "/"

            if ".." in normalized_path.split("/"):
                raise HTTPException(status_code=400, detail="Chemin invalide")

            cache_key = (bucket_name, normalized_path, recursive)
            cached = self._cache_get(self._full_list_cache, cache_key)
            if cached is None:
                def list_objects_full() -> list[FullFileItem]:
                    objects = self.minio.list_objects(
                        bucket_name, prefix=normalized_path, recursive=recursive
                    )
                    items: list[FullFileItem] = []

                    for obj in objects:
                        if obj.object_name == normalized_path:
                            continue
                        if not obj.object_name:
                            continue

                        name = obj.object_name.removeprefix(normalized_path).rstrip("/")
                        is_dir = obj.object_name.endswith("/")

                        etag = obj.etag
                        content_type = obj.content_type
                        size = obj.size if not is_dir else None

                        last_modified = obj.last_modified if obj.last_modified else None
                        if is_dir and obj.metadata:
                            lm = obj.metadata.get("x-amz-meta-last_modified")
                            if lm:
                                last_modified = datetime.datetime.fromisoformat(lm)

                        items.append(
                            FullFileItem(
                                name=name,
                                size=size,
                                is_dir=is_dir,
                                last_modified=last_modified or datetime.datetime.now(),
                                etag=etag,
                                content_type=content_type,
                            )
                        )

                    items.sort(key=lambda x: (not x.is_dir, x.name.lower()))
                    return items

                items = await run_in_threadpool(list_objects_full)
                if len(items) <= self._CACHE_MAX_ITEMS:
                    self._cache_set(self._full_list_cache, cache_key, items)
            else:
                items = cached

            return FullFileTreeResponse(
                path="/" + normalized_path if normalized_path else "/",
                items=items,
                total_items=len(items),
            )

        except S3Error as e:
            logger.error(f"Échec de la liste complète du chemin {path}: {e}")
            raise HTTPException(
                status_code=404 if e.code == "NoSuchKey" else 500,
                detail=f"Impossible de lister le chemin: {str(e)}",
            )


def get_minio_service(request: Request) -> MinioService:
    """Fournit une instance de MinioService avec le client Minio de l'app."""
    # Prefer the singleton created at startup so we can reuse internal caches and
    # avoid recreating service wrappers for every request.
    existing = getattr(request.app.state, "minio_service", None)
    if existing is not None:
        return existing
    # Fallback (tests or older app.state setup).
    return MinioService(request.app.state.minio_client)
