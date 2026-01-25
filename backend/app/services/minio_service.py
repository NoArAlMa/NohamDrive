from minio import Minio
from minio.error import S3Error
from app.schemas.file_tree import SimpleFileItem, SimpleFileTreeResponse
from app.services.minio.bucket_service import BucketService
from app.services.minio.download_service import DownloadService
from app.services.minio.object_service import ObjectService
from core.logging import setup_logger
from datetime import datetime
from fastapi import HTTPException, Request

# Initialisation du logger
logger = setup_logger(__name__)


class MinioService:
    def __init__(self, minio: Minio):
        self.minio: Minio = minio
        self.bucket_service = BucketService(self.minio)
        self.object_service = ObjectService(self.minio, self.bucket_service)
        self.download_service = DownloadService(self.minio, self.bucket_service)

    async def simple_list_path(
        self, bucket_name: str, path: str = "", limit: int = 30
    ) -> SimpleFileTreeResponse:
        try:
            normalized_path = path.strip("/")
            if normalized_path:
                normalized_path += "/"

            objects = self.minio.list_objects(
                bucket_name,
                prefix=normalized_path,
                recursive=False,
            )

            items = []

            for obj in objects:
                # Ignore le dossier courant
                if obj.object_name == normalized_path:
                    continue

                # Nom affiché (sans le chemin parent)
                if obj.object_name:
                    name = obj.object_name.removeprefix(normalized_path).rstrip("/")

                items.append(
                    SimpleFileItem(
                        name=name,
                        size=None if obj.is_dir else obj.size,
                        is_dir=obj.is_dir,
                        last_modified=obj.last_modified or datetime.min,
                    )
                )

            items.sort(key=lambda x: (not x.is_dir, x.name.lower()))

            return SimpleFileTreeResponse(
                path="/" + normalized_path if normalized_path else "/",
                items=items[:limit],
            )

        except S3Error as e:
            logger.error(f"Échec de la liste du chemin {path} : {e}")
            raise HTTPException(
                status_code=404 if e.code == "NoSuchKey" else 500,
                detail="Impossible de lister le chemin",
            )


def get_minio_service(request: Request) -> MinioService:
    """Fournit une instance de MinioService avec le client Minio de l'app."""
    return MinioService(request.app.state.minio_client)
