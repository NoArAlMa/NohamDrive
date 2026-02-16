import datetime
from fastapi import HTTPException, Query, Request
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

from app.utils.minio_utils import MinioUtils
from core.logging import setup_logger


# Initialisation du logger
logger = setup_logger(__name__)


class MinioService:
    def __init__(self, minio: Minio):
        self.minio: Minio = minio
        self.bucket_service = BucketService(minio)
        self.object_service = ObjectService(minio, self.bucket_service)
        self.download_service = DownloadService(minio, self.bucket_service)

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

            path_type = await MinioUtils.resolve_path_type(
                minio_client=self.minio,
                bucket_name=bucket_name,
                path=normalized_path,
            )

            if path_type == "not_found":
                raise HTTPException(status_code=404, detail="Path not found")

            if path_type == "file":
                raise HTTPException(status_code=400, detail="Not a directory")

            objects = self.minio.list_objects(
                bucket_name,
                prefix=normalized_path,
                recursive=False,
            )

            items: list[SimpleFileItem] = []

            for obj in objects:
                # Ignore le dossier courant
                if obj.object_name == normalized_path:
                    continue

                # Nom affiché (sans le chemin parent)
                if obj.object_name:
                    name = obj.object_name.removeprefix(normalized_path).rstrip("/")
                    is_dir = obj.object_name.endswith("/")

                last_modified = obj.last_modified

                if is_dir:
                    try:
                        if obj.object_name:
                            stat = self.minio.stat_object(bucket_name, obj.object_name)
                            lm = None
                            if stat.metadata is not None:
                                lm = stat.metadata.get("x-amz-meta-last_modified")
                        if lm:
                            last_modified = datetime.datetime.fromisoformat(lm)
                    except Exception:
                        last_modified = None

                items.append(
                    SimpleFileItem(
                        name=name,
                        size=None if is_dir else obj.size,
                        is_dir=is_dir,
                        last_modified=last_modified or datetime.datetime.now(),
                    )
                )

            items.sort(key=lambda x: (not x.is_dir, (x.name or "").lower()))

            total_items = len(items)
            total_pages = (total_items + per_page - 1) // per_page
            start = (page - 1) * per_page
            end = start + per_page
            paginated_items = items[start:end]

            return SimpleFileTreeResponse(
                path="/" + normalized_path if normalized_path else "/",
                items=paginated_items,
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

    # Dans MinioService (à ajouter)

    async def full_list_path(
        self,
        path: str = "",
        user_id: int = 1,
        recursive: bool = False,
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

            # Vérifie que le chemin existe et est un dossier
            path_type = await MinioUtils.resolve_path_type(
                self.minio, bucket_name, normalized_path
            )
            if path_type == "not_found":
                raise HTTPException(status_code=404, detail="Chemin introuvable")
            if path_type == "file":
                raise HTTPException(status_code=400, detail="Ce n'est pas un dossier")

            objects = self.minio.list_objects(
                bucket_name, prefix=normalized_path, recursive=recursive
            )
            items = []

            for obj in objects:
                # Ignore le dossier courant
                if obj.object_name == normalized_path:
                    continue

                # Nom affiché (relatif au path)
                name = (
                    obj.object_name.removeprefix(normalized_path).rstrip("/")
                    if obj.object_name
                    else ""
                )
                is_dir = obj.object_name.endswith("/") if obj.object_name else False

                # Récupère les métadonnées étendues
                if obj.object_name:
                    stat = self.minio.stat_object(bucket_name, obj.object_name)
                last_modified = stat.last_modified
                etag = stat.etag  # Hash du contenu
                content_type = stat.content_type
                size = stat.size if not is_dir else None

                # Pour les dossiers, essaye de récupérer last_modified depuis les métadonnées
                if is_dir:
                    try:
                        if (
                            stat.metadata
                            and "x-amz-meta-last_modified" in stat.metadata
                        ):
                            last_modified = datetime.datetime.fromisoformat(
                                stat.metadata["x-amz-meta-last_modified"]
                            )
                    except Exception:
                        last_modified = datetime.datetime.now()

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
    return MinioService(request.app.state.minio_client)
