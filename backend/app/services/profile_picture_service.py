from __future__ import annotations

from io import BytesIO

from fastapi import HTTPException, Request, UploadFile, status
from fastapi.concurrency import run_in_threadpool
from minio.error import S3Error

from app.services.minio.minio_service import MinioService, get_minio_service
from app.utils.user_utils import UserUtils


class ProfilePictureService:
    """
    Stocke l'avatar de l'utilisateur dans son bucket MinIO.

    - Objet unique (pas de conflits): "__profile__/avatar"
    - Par défaut: SVG généré à partir du full_name (initiales).
    - Si l'utilisateur upload un fichier: on écrase l'objet.
    """

    _OBJECT_NAME = "__profile__/avatar"
    _MAX_UPLOAD_BYTES = 5 * 1024 * 1024

    def __init__(self, minio_service: MinioService):
        self._minio_service = minio_service
        self._minio = minio_service.minio
        self._bucket_service = minio_service.bucket_service

    async def ensure_default_exists(self, *, user_id: int, full_name: str) -> None:
        bucket_name = await self._bucket_service.ensure_bucket_exists(user_id)

        def stat():
            return self._minio.stat_object(bucket_name, self._OBJECT_NAME)

        try:
            await run_in_threadpool(stat)
            return
        except S3Error as e:
            if e.code != "NoSuchKey":
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Erreur stockage (avatar)",
                )

        svg = UserUtils.generate_profile_picture_svg(full_name)
        data = svg.encode("utf-8")

        def put():
            self._minio.put_object(
                bucket_name=bucket_name,
                object_name=self._OBJECT_NAME,
                data=BytesIO(data),
                length=len(data),
                content_type="image/svg+xml; charset=utf-8",
            )

        await run_in_threadpool(put)

    async def get_picture(self, *, user_id: int, full_name: str) -> tuple[bytes, str]:
        bucket_name = await self._bucket_service.ensure_bucket_exists(user_id)

        def get():
            return self._minio.get_object(bucket_name, self._OBJECT_NAME)

        try:
            response = await run_in_threadpool(get)
        except S3Error as e:
            if e.code != "NoSuchKey":
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Erreur stockage (avatar)",
                )
            await self.ensure_default_exists(user_id=user_id, full_name=full_name)
            svg = UserUtils.generate_profile_picture_svg(full_name)
            return svg.encode("utf-8"), "image/svg+xml; charset=utf-8"

        try:
            data = await run_in_threadpool(response.read)
            try:
                stat = await run_in_threadpool(
                    lambda: self._minio.stat_object(bucket_name, self._OBJECT_NAME)
                )
                content_type = stat.content_type or "application/octet-stream"
            except Exception:
                content_type = "application/octet-stream"
            return data, content_type
        finally:
            response.close()
            response.release_conn()

    async def set_picture(self, *, user_id: int, file: UploadFile) -> dict:
        if not file or not file.filename:
            raise HTTPException(status_code=400, detail="Fichier invalide")

        content_type = file.content_type or "application/octet-stream"
        if not (
            content_type.startswith("image/")
            or content_type in {"application/octet-stream", "image/svg+xml"}
        ):
            raise HTTPException(status_code=415, detail="Type de fichier non supporté")

        raw = await file.read()
        if not raw:
            raise HTTPException(status_code=400, detail="Fichier vide")
        if len(raw) > self._MAX_UPLOAD_BYTES:
            raise HTTPException(status_code=413, detail="Avatar trop volumineux (5MB)")

        bucket_name = await self._bucket_service.ensure_bucket_exists(user_id)

        def put():
            self._minio.put_object(
                bucket_name=bucket_name,
                object_name=self._OBJECT_NAME,
                data=BytesIO(raw),
                length=len(raw),
                content_type=content_type,
            )

        try:
            await run_in_threadpool(put)
        except S3Error:
            raise HTTPException(
                status_code=500, detail="Échec de l'upload de l'avatar"
            )

        return {"object_name": self._OBJECT_NAME, "content_type": content_type}


def get_profile_picture_service(request: Request) -> ProfilePictureService:
    return ProfilePictureService(get_minio_service(request))

