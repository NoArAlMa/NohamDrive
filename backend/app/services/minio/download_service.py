from typing import Iterator, cast
import zipfile
from fastapi import HTTPException, UploadFile
from fastapi.responses import StreamingResponse
from minio import Minio, S3Error
from app.services.minio.bucket_service import BucketService
from app.utils.minio_utils import MinioUtils
from core.logging import setup_logger
import zipstream
import mimetypes

logger = setup_logger(__name__)


class DownloadService:
    def __init__(self, minio: Minio, bucket_service: BucketService) -> None:
        self.minio = minio
        self.bucket_service = bucket_service

    async def upload_file(self, user_id: int, file: UploadFile, path: str = ""):
        """
        Upload un fichier dans MinIO dans le dossier spécifié.
        """

        if not file or not file.filename:
            raise HTTPException(400, "Fichier invalide")

        bucket_name = await self.bucket_service.get_user_bucket(user_id)
        normalized_path = MinioUtils.normalize_path(path, is_folder=False)
        object_name_base = MinioUtils.sanitize_filename(file.filename)

        object_name = MinioUtils.generate_available_name(
            minio_client=self.minio,
            bucket_name=bucket_name,
            base_name=object_name_base,
            parent_path=normalized_path,
            is_folder=False,
        )

        content_type = file.content_type or "application/octet-stream"

        try:
            file.file.seek(0, 2)
            file_size = file.file.tell()
            file.file.seek(0)

            self.minio.put_object(
                bucket_name=bucket_name,
                object_name=object_name,
                data=file.file,
                length=file_size,
                content_type=content_type,
            )

            return {"name": object_name}

        except S3Error as e:
            status_code = (
                400 if e.code in ["InvalidArgument", "EntityTooLarge"] else 500
            )

            raise HTTPException(
                status_code=status_code,
                detail=f"Échec de l'upload: {str(e)}",
            )

    # TODO : FONCTIONNE PAS !!! =>>>

    async def download_object(
        self, user_id: int, object_name: str
    ) -> StreamingResponse:
        """
        Télécharge un fichier ou un dossier depuis MinIO.
        """
        bucket_name = await self.bucket_service.get_user_bucket(user_id)

        # Normalisation du chemin
        object_name = MinioUtils.normalize_path(
            object_name, is_folder=object_name.endswith("/")
        )

        def try_get_file():
            try:
                return self.minio.get_object(bucket_name, object_name)
            except S3Error:
                return None

        response = try_get_file()

        if response:
            filename = object_name.split("/")[-1]

            def file_iterator():
                try:
                    for chunk in response.stream(1024 * 1024):
                        yield bytes(chunk)
                finally:
                    response.close()
                    response.release_conn()

            return StreamingResponse(
                file_iterator(),
                media_type="application/octet-stream",
                headers={"Content-Disposition": f'attachment; filename="{filename}"'},
            )

        prefix = object_name.rstrip("/") + "/"

        objects_iter = self.minio.list_objects(
            bucket_name, prefix=prefix, recursive=True
        )

        def zip_iterator() -> Iterator[bytes]:
            z = zipstream.ZipFile(mode="w", compression=zipfile.ZIP_DEFLATED)

            for obj in objects_iter:
                name = obj.object_name

                if not name or name.endswith("/"):
                    continue

                try:
                    response = self.minio.get_object(bucket_name, name)
                except S3Error:
                    continue

                relative_path = name[len(prefix) :]

                def stream_file(r=response):
                    try:
                        for chunk in r.stream(1024 * 1024):
                            yield bytes(chunk)
                    finally:
                        r.close()
                        r.release_conn()

                z.write_iter(relative_path, stream_file())

            yield from cast(Iterator[bytes], z)

        zip_name = f"{object_name.rstrip('/')}.zip"

        return StreamingResponse(
            zip_iterator(),
            media_type="application/zip",
            headers={"Content-Disposition": f'attachment; filename="{zip_name}"'},
        )

    async def preview_object(
        self,
        user_id: int,
        object_name: str,
    ) -> StreamingResponse:
        """
        Prévisualise un fichier depuis MinIO.
        """

        bucket_name = await self.bucket_service.get_user_bucket(user_id)

        object_name = MinioUtils.normalize_path(object_name, is_folder=False)

        if ".." in object_name:
            raise HTTPException(status_code=400, detail="Chemin invalide.")

        try:
            stat = self.minio.stat_object(bucket_name, object_name)

            def file_iterator() -> Iterator[bytes]:
                response = self.minio.get_object(bucket_name, object_name)
                try:
                    for chunk in response.stream(1024 * 1024):
                        yield cast(bytes, chunk)
                finally:
                    response.close()
                    response.release_conn()

            filename = object_name.split("/")[-1]

            content_type = stat.content_type
            if not content_type or content_type == "application/octet-stream":
                guessed_type, _ = mimetypes.guess_type(filename)
                content_type = guessed_type or "application/octet-stream"

            return StreamingResponse(
                file_iterator(),
                media_type=content_type,
                headers={
                    "Content-Disposition": f'inline; filename="{filename}"',
                    "Content-Length": str(stat.size),
                },
            )

        except S3Error as e:
            logger.error(
                "Preview failed",
                extra={
                    "user_id": user_id,
                    "object_name": object_name,
                    "error": str(e),
                },
            )
            raise HTTPException(
                status_code=404,
                detail="Fichier introuvable.",
            )
