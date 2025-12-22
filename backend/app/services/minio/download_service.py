from datetime import datetime
import io
import zipfile
from fastapi import HTTPException, UploadFile
from fastapi.responses import StreamingResponse
from minio import Minio, S3Error
from app.schemas.files import FileMetadata
from app.services.minio.bucket_service import BucketService
from app.utils.minio_utils import MinioUtils
from core.logging import setup_logger


logger = setup_logger(__name__)


class DownloadService:
    def __init__(self, minio: Minio, bucket_service: BucketService) -> None:
        self.minio = minio
        self.bucket_service = bucket_service

    async def upload_file(
        self, user_id: int, file: UploadFile, path: str = ""
    ) -> tuple:
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
                    upload_date=datetime.now(),
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
        Télécharge un fichier ou un dossier depuis MinIO.
        """
        bucket_name = await self.bucket_service.get_user_bucket(user_id)

        # Normalisation du chemin
        object_name = MinioUtils.normalize_path(
            object_name, is_folder=object_name.endswith("/")
        )

        try:
            # Vérifie si c'est un fichier existant
            try:
                obj = self.minio.stat_object(bucket_name, object_name)
                is_file = True
            except S3Error as e:
                if e.code == "NoSuchKey":
                    is_file = False
                else:
                    raise

            if is_file:
                # Streaming direct du fichier
                file_stream = self.minio.get_object(bucket_name, object_name)
                return StreamingResponse(
                    content=file_stream.stream(amt=1024 * 1024),  # chunks de 1 Mo
                    media_type=obj.content_type or "application/octet-stream",
                    headers={
                        "Content-Disposition": f"attachment; filename={object_name.split('/')[-1]}",
                        "Content-Length": str(obj.size),
                    },
                )

            # C’est un dossier → on crée un ZIP
            prefix = object_name.rstrip("/") + "/"
            objects = list(
                self.minio.list_objects(bucket_name, prefix=prefix, recursive=True)
            )

            if not objects:
                raise HTTPException(
                    404, detail=f"Objet ou dossier '{object_name}' introuvable."
                )

            zip_buffer = io.BytesIO()
            with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zipf:
                for obj in objects:
                    if not obj.object_name or obj.object_name.endswith("/"):
                        continue
                    data = self.minio.get_object(bucket_name, obj.object_name)
                    file_bytes = data.read()
                    relative_name = obj.object_name[
                        len(prefix) :
                    ]  # chemin relatif dans ZIP
                    zipf.writestr(relative_name, file_bytes)

            zip_buffer.seek(0)

            return StreamingResponse(
                zip_buffer,
                media_type="application/zip",
                headers={
                    "Content-Disposition": f"attachment; filename={object_name.rstrip('/')}.zip",
                    "Content-Length": str(zip_buffer.getbuffer().nbytes),
                },
            )

        except S3Error as e:
            logger.error(
                "Échec du téléchargement",
                extra={"user_id": user_id, "object_name": object_name, "error": str(e)},
            )
            raise HTTPException(500, detail=f"Erreur lors du téléchargement: {str(e)}")
