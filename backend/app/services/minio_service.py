from minio import Minio
from minio.error import S3Error
from app.schemas.files import FileMetadata
from app.schemas.file_tree import SimpleFileItem, SimpleFileTreeResponse
from core.logging import setup_logger
import uuid
from datetime import datetime
from fastapi import UploadFile, HTTPException, status, Request
from fastapi.responses import StreamingResponse


logger = setup_logger(__name__)


class MinioService:
    def __init__(self, minio):
        self.minio: Minio = minio

    async def get_user_bucket(self, user_id: int) -> str:
        """Retourne le nom du bucket utilisateur."""
        return f"user-{user_id}"

    async def ensure_bucket_exists(self, user_id: int) -> str:
        """
        Crée le bucket utilisateur s'il n'existe pas.

        NOTES : Fonction temporaire le temps de créer le système d'auth
        """
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
        bucket_name = await self.ensure_bucket_exists(
            user_id
        )  # TODO : Mieux gérer le nom des buckets, attribution ect...
        object_name = f"{uuid.uuid4()}_{file.filename}"  # TODO : Actuellement on peut créer plusieurs fichiers avec le même nom

        try:
            # Upload en streaming
            self.minio.put_object(
                bucket_name,
                object_name,
                file.file,
                length=-1,  # Streaming
                part_size=10 * 1024 * 1024,  # 10 Mo par partie
                content_type=file.content_type or "application/octet-stream",
            )

            return FileMetadata(
                filename=file.filename,
                size=file.size,
                content_type=file.content_type,
                upload_date=datetime.now(),
                bucket=bucket_name,
                object_name=object_name,
            )
        except S3Error as e:
            logger.error(f"Échec de l'upload pour {file.filename}: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Échec de l'upload: {str(e)}",
            )

    async def simple_list_path(
        self, bucket_name: str, path: str = "", limit: int = 30
    ) -> SimpleFileTreeResponse:
        """
        Liste les objets dans un bucket MinIO, version ultra-simplifiée.
        Args:
            bucket_name: Nom du bucket.
            path: Préfixe (ex: "dossier/").
        Returns:
            SimpleFileTreeResponse: Liste brute des objets .
        """
        try:
            objects = list(
                self.minio.list_objects(
                    bucket_name,
                    prefix=path,
                    recursive=False,
                )
            )

            items = []
            for obj in objects:
                items.append(
                    SimpleFileItem(
                        name=obj.object_name,
                        size=obj.size or None,
                        is_dir=obj.is_dir,
                        last_modified=obj.last_modified or datetime.min,
                    )
                )

            return SimpleFileTreeResponse(path=path or "/", items=items)

        except S3Error as e:
            logger.error(f"Échec de la liste du chemin {path} : {e}")
            raise HTTPException(
                status_code=404 if "NoSuchKey" in str(e) else 500,
                detail=f"Impossible de lister le chemin : {str(e)}",
            )

    async def download_file(self, user_id: int, object_name: str) -> StreamingResponse:
        """
        Télécharge un fichier depuis MinIO.

        Args:
            user_id: ID de l'utilisateur (pour déterminer le bucket si non fourni).
            object_name: Nom de l'objet dans MinIO.
            bucket_name: Nom du bucket (optionnel, sinon déduit de user_id).

        Returns:
            StreamingResponse: Flux du fichier à télécharger.

        Raises:
            HTTPException: 404 si le fichier ou le bucket n'existe pas.
                          403 si accès non autorisé.
                          500 en cas d'erreur interne.
        """
        try:
            bucket_name = await self.get_user_bucket(user_id)

            # Vérifie que le bucket existe
            if not self.minio.bucket_exists(bucket_name):
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Bucket non trouvé.",
                )

            # Récupère les métadonnées de l'objet pour vérifier son existence
            try:
                # On nettoie le chemin au cas où il y aurait des pépins
                if ".." in object_name or object_name.startswith("/"):
                    raise HTTPException(status_code=400, detail="Chemin invalide.")

                obj = self.minio.stat_object(bucket_name, object_name)
            except S3Error as e:
                if e.code == "NoSuchKey":
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"Fichier {object_name} non trouvé.",
                    )
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Erreur lors de la vérification du fichier: {str(e)}",
                )

            # Stream le fichier en chunks pour éviter de tout charger en mémoire
            file_stream = self.minio.get_object(bucket_name, object_name)

            # Construit la réponse en streaming
            return StreamingResponse(
                content=file_stream.stream(amt=1024 * 1024),  # Chunks de 1 Mo
                media_type=obj.content_type or "application/octet-stream",
                headers={
                    "Content-Disposition": f"attachment; filename={object_name.split('/')[-1]}",
                    "Content-Length": str(obj.size),
                },
            )

        except S3Error as e:
            logger.error(
                "Échec du téléchargement",
                extra={"user_id": user_id, "object_name": object_name, "error": str(e)},
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erreur lors du téléchargement: {str(e)}",
            )


def get_minio_service(request: Request) -> MinioService:
    """Fournit une instance de MinioService avec le client Minio de l'app."""
    return MinioService(request.app.state.minio_client)
