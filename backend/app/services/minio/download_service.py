from datetime import datetime
from typing import Iterator, cast
import zipfile
from fastapi import HTTPException, UploadFile
from fastapi.responses import StreamingResponse
from minio import Minio, S3Error
from app.schemas.files import FileMetadata
from app.services.minio.bucket_service import BucketService
from app.utils.minio_utils import MinioUtils
from core.logging import setup_logger
import zipstream


logger = setup_logger(__name__)


class DownloadService:
    def __init__(self, minio: Minio, bucket_service: BucketService) -> None:
        self.minio = minio
        self.bucket_service = bucket_service

    async def upload_file(
        self, user_id: int, file: UploadFile, path: str = ""
    ) -> tuple[str, FileMetadata]:
        """
        Upload un fichier dans MinIO dans le dossier spécifié.
        Args:
            user_id: ID de l'utilisateur
            file: FastAPI UploadFile
            path: chemin relatif dans le bucket (ex: "dossier1/dossier2")
        Returns:
            FileMetadata
        """
        bucket_name = await self.bucket_service.ensure_bucket_exists(user_id)

        normalized_path = MinioUtils.normalize_path(path, is_folder=False)

        # Sécurisation du nom de fichier
        if file.filename:
            object_name_base = MinioUtils.sanitize_filename(file.filename)

        # Gestion des doublons façon Windows
        object_name = MinioUtils.generate_available_name(
            minio_client=self.minio,
            bucket_name=bucket_name,
            base_name=object_name_base,
            parent_path=normalized_path,
            is_folder=False,
        )

        logger.info("Nom du fichier : %s", object_name)

        # Upload en streaming
        content_type = file.content_type or "application/octet-stream"
        try:
            self.minio.put_object(
                bucket_name,
                object_name,
                file.file,
                length=-1,
                part_size=10 * 1024 * 1024,
                content_type=content_type,
            )

            # Récupération de la taille réelle
            stat = self.minio.stat_object(bucket_name, object_name)

            return (
                f"{file.filename} uploadé",
                FileMetadata(
                    filename=file.filename,
                    size=stat.size,
                    content_type=content_type,
                    upload_date=datetime.now().isoformat(),
                    bucket=bucket_name,
                    object_name=object_name,
                ),
            )

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
        Télécharge un fichier ou un dossier depuis MinIO (streaming propre).
        """
        bucket_name = await self.bucket_service.get_user_bucket(user_id)

        # Normalisation du chemin
        object_name = MinioUtils.normalize_path(
            object_name, is_folder=object_name.endswith("/")
        )

        try:
            # --- Détection fichier vs dossier ---
            try:
                stat = self.minio.stat_object(bucket_name, object_name)
                is_file = True
            except S3Error as e:
                if e.code == "NoSuchKey":
                    is_file = False
                else:
                    raise


            if is_file:

                def file_iterator() -> Iterator[bytes]:
                    response = self.minio.get_object(bucket_name, object_name)
                    try:
                        for chunk in response.stream(1024 * 1024):
                            yield cast(bytes, chunk)
                    finally:
                        response.close()
                        response.release_conn()

                filename = object_name.split("/")[-1]

                return StreamingResponse(
                    file_iterator(),
                    media_type=stat.content_type or "application/octet-stream",
                    headers={
                        "Content-Disposition": f'attachment; filename="{filename}"'
                    },
                )


            prefix = object_name.rstrip("/") + "/"

            objects = list(
                self.minio.list_objects(bucket_name, prefix=prefix, recursive=True)
            )

            if not objects:
                raise HTTPException(
                    status_code=404,
                    detail=f"Objet ou dossier '{object_name}' introuvable.",
                )

            def zip_iterator() -> Iterator[bytes]:
                z = zipstream.ZipFile(mode="w", compression=zipfile.ZIP_DEFLATED)

                # Préparer tous les générateurs avant le yield
                for obj in objects:
                    if obj.object_name:
                        if obj.object_name.endswith("/"):
                            continue

                        response = self.minio.get_object(bucket_name, obj.object_name)

                    # générateur indépendant
                    def stream_file(resp=response) -> Iterator[bytes]:
                        try:
                            for chunk in resp.stream(1024 * 1024):
                                yield bytes(chunk)
                        finally:
                            resp.close()
                            resp.release_conn()

                    if obj.object_name:
                        relative_path = obj.object_name[len(prefix) :]
                    z.write_iter(relative_path, stream_file())

                # itération finale pour produire le ZIP
                for chunk in z:
                    yield cast(bytes, chunk)

            zip_name = f"{object_name.rstrip('/')}.zip"

            return StreamingResponse(
                zip_iterator(),
                media_type="application/zip",
                headers={"Content-Disposition": f'attachment; filename="{zip_name}"'},
            )

        except S3Error as e:
            logger.error(
                "Échec du téléchargement",
                extra={
                    "user_id": user_id,
                    "object_name": object_name,
                    "error": str(e),
                },
            )
            raise HTTPException(
                status_code=500,
                detail=f"Erreur lors du téléchargement: {str(e)}",
            )
