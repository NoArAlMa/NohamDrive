from minio.error import S3Error
from core.minio_client import get_minio_client
from app.schemas.files import FileMetadata
import logging
import uuid
from datetime import datetime
from fastapi import UploadFile, HTTPException, status

logger = logging.getLogger(__name__)


class FileService:
    def __init__(self):
        self.minio = get_minio_client()

    async def get_user_bucket(self, user_id: int) -> str:
        """Retourne le nom du bucket utilisateur."""
        return f"user-{user_id}"

    async def ensure_bucket_exists(self, user_id: int) -> str:
        """Crée le bucket utilisateur s'il n'existe pas."""
        bucket_name = await self.get_user_bucket(user_id)
        if not self.minio.bucket_exists(bucket_name):
            self.minio.make_bucket(bucket_name)
            logger.info(f"Bucket {bucket_name} créé pour l'utilisateur {user_id}.")
        return bucket_name

    async def upload_file(self, user_id: int, file: UploadFile) -> FileMetadata:
        """
        Upload un fichier dans MinIO.
        Args:
            user_id: ID de l'utilisateur.
            file: Fichier à uploader (FastAPI UploadFile).
        Returns:
            FileMetadata: Métadonnées du fichier uploadé.
        """
        bucket_name = self.ensure_bucket_exists(user_id)
        object_name = f"{uuid.uuid4()}_{file.filename}"

        try:
            # Upload en streaming
            self.minio.put_object(
                bucket_name,
                object_name,
                file.file,
                length=-1,  # Streaming
                part_size=10 * 1024 * 1024,  # 10 Mo par partie
                content_type=file.content_type,
            )

            return FileMetadata(
                filename=file.filename,
                size=file.size,
                content_type=file.content_type,
                upload_date=datetime.utcnow(),
                bucket=bucket_name,
                object_name=object_name,
            )
        except S3Error as e:
            logger.error(f"Échec de l'upload pour {file.filename}: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Échec de l'upload: {str(e)}",
            )


def get_file_service() -> FileService:
    """Fournit une instance de FileService."""
    return FileService()
