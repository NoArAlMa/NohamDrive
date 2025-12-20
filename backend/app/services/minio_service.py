from minio import Minio
from minio.error import S3Error
from app.schemas.files import FileMetadata
from app.schemas.file_tree import SimpleFileItem, SimpleFileTreeResponse
from minio.deleteobjects import DeleteObject
from minio.commonconfig import CopySource
from core.logging import setup_logger
from datetime import datetime
from fastapi import UploadFile, HTTPException, status, Request
from fastapi.responses import StreamingResponse
import io
import re


# Initialisation du logger
logger = setup_logger(__name__)


class MinioService:
    def __init__(self, minio: Minio):
        self.minio: Minio = minio

    async def get_user_bucket(self, user_id: int) -> str:
        """Retourne le nom du bucket utilisateur."""
        return f"user-{user_id}"

    async def create_user_bucket(self, user_id: int) -> str:
        """
        Crée le bucket d'un nouvel utilisateur s'il n'existe pas et en retourne le nom.
        """
        bucket_name = await self.get_user_bucket(user_id)
        if not self.minio.bucket_exists(bucket_name):
            self.minio.make_bucket(bucket_name)
            logger.info(f"Bucket {bucket_name} créé pour l'utilisateur {user_id}.")
        return bucket_name

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

    async def upload_file(
        self, user_id: int, file: UploadFile, path: str = ""
    ) -> FileMetadata:
        """
        Upload un fichier dans MinIO dans le dossier spécifié.
        Args:
            user_id: ID de l'utilisateur
            file: FastAPI UploadFile
            path: chemin relatif dans le bucket (ex: "dossier1/dossier2")
        Returns:
            FileMetadata
        """
        bucket_name = await self.ensure_bucket_exists(user_id)

        # Normalisation et sécurité du chemin
        normalized_path = path.strip("/").rstrip("/")
        if ".." in normalized_path or normalized_path.startswith("/"):
            raise HTTPException(status_code=400, detail="Chemin invalide.")
        if normalized_path:
            normalized_path += "/"

        # Sécurisation du nom de fichier

        if file.filename:
            base_name, ext = (
                file.filename.rsplit(".", 1)
                if "." in file.filename
                else (file.filename, "")
            )
            base_name = re.sub(r"[^a-zA-Z0-9_.-]", "_", base_name)  # Nettoyage
            ext = f".{ext}" if ext else ""
            object_name = f"{normalized_path}{base_name}{ext}"

        # Gestion des doublons façon Windows
        counter = 1
        while True:
            try:
                self.minio.stat_object(bucket_name, object_name)
                # fichier existe → on ajoute (1), (2), etc.
                object_name = f"{normalized_path}{base_name} ({counter}){ext}"
                counter += 1
            except S3Error as e:
                if e.code == "NoSuchKey":
                    break  # Nom disponible
                else:
                    raise HTTPException(
                        status_code=500,
                        detail=f"Erreur lors de la vérification du fichier : {str(e)}",
                    )

        logger.info("Nom du fichier : %s ", object_name)
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

            return FileMetadata(
                filename=file.filename,
                size=stat.size,
                content_type=content_type,
                upload_date=datetime.now(),
                bucket=bucket_name,
                object_name=object_name,
            )

        except S3Error as e:
            status_code = (
                400 if e.code in ["InvalidArgument", "EntityTooLarge"] else 500
            )
            raise HTTPException(
                status_code=status_code,
                detail=f"Échec de l'upload: {str(e)}",
            )

    async def delete_file(self, user_id: int, object_name: str):
        bucket_name = await self.get_user_bucket(user_id)

        if ".." in object_name or object_name.startswith("/"):
            raise HTTPException(status_code=400, detail="Chemin invalide.")

        try:
            self.minio.stat_object(bucket_name, object_name)
        except S3Error as e:
            if e.code == "NoSuchKey":
                raise HTTPException(status_code=404, detail="Fichier non trouvé")
            else:
                raise HTTPException(status_code=500, detail=f"Erreur : {str(e)}")

        try:
            self.minio.remove_object(bucket_name, object_name)
            return f"Fichier {object_name} supprimé avec succès"
        except S3Error as e:
            raise HTTPException(
                status_code=500, detail=f"Erreur lors de la suppression : {str(e)}"
            )

    async def delete_folder(self, user_id: int, folder_path: str):
        bucket_name = await self.get_user_bucket(user_id)

        # Normalisation
        folder_path = folder_path.strip("/").rstrip("/") + "/"
        if ".." in folder_path or folder_path.startswith("/"):
            raise HTTPException(status_code=400, detail="Chemin invalide.")

        objects_to_delete = self.minio.list_objects(
            bucket_name, prefix=folder_path, recursive=True
        )

        to_delete = [
            DeleteObject(obj.object_name)
            for obj in objects_to_delete
            if obj.object_name
        ]

        if not to_delete:
            raise HTTPException(status_code=404, detail="Dossier vide ou inexistant")

        try:
            # Supprime tous les objets et consomme le générateur
            errors = list(self.minio.remove_objects(bucket_name, to_delete))

            # Log des éventuelles erreurs
            if errors:
                raise HTTPException(
                    status_code=500,
                    detail="Erreur lors de la suppression de certains objets",
                )

            return {
                "detail": f"Dossier {folder_path} supprimé avec {len(to_delete)} objets"
            }

        except S3Error as e:
            raise HTTPException(
                status_code=500, detail=f"Erreur lors de la suppression : {str(e)}"
            )

    async def create_folder(
        self, user_id: int, current_path: str, folder_path: str
    ) -> str:
        """
        Crée un dossier dans MinIO au chemin spécifié.

        Args:
            user_id: ID de l'utilisateur (pour déterminer le bucket).
            current_path: Chemin actuel (ex: "dossier_parent/").
            folder_path: Chemin relatif du nouveau dossier (ex: "nouveau_dossier").

        Returns:
            str: Chemin complet du dossier créé.

        Raises:
            HTTPException: 400 si le chemin est invalide ou si le dossier existe déjà.
                        500 en cas d'erreur interne.
        """
        bucket_name = await self.get_user_bucket(user_id)

        # Nettoie et normalise le chemin
        if not current_path.endswith("/"):
            current_path += "/"
        full_path = f"{current_path.rstrip('/')}/{folder_path.strip('/')}/"

        if not full_path.endswith("/"):
            full_path += "/"
        logger.info(full_path)
        # Vérifie que le chemin est valide (pas de ".." ou chemin absolu)
        if ".." in full_path:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Chemin invalide (accès non autorisé).",
            )

        try:
            # On vérifie si un objet avec ce préfixe existe déjà
            self.minio.stat_object(bucket_name, full_path)

            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Le dossier '{full_path}' existe déjà.",
            )
        except S3Error as e:
            if e.code != "NoSuchKey":
                logger.error(
                    f"Erreur lors de la vérification du dossier {full_path}: {e}"
                )
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Impossible de vérifier le dossier.",
                )

        # Crée le dossier
        try:
            self.minio.put_object(
                bucket_name,
                full_path,
                io.BytesIO(b""),  # Contenu vide
                0,
                content_type="application/x-directory",
            )
            logger.info(f"Dossier [bold]{full_path}[/bold] créé dans {bucket_name}")
            return full_path
        except S3Error as e:
            logger.error(f"Échec de la création du dossier {full_path}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Impossible de créer le dossier: {str(e)}",
            )

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

    async def rename(self, user_id: int, path: str, new_name: str):
        bucket_name = await self.get_user_bucket(user_id)

        if ".." in path or ".." in new_name or "/" in new_name:
            raise HTTPException(status_code=400, detail="Chemin invalide")

        path = path.lstrip("/")
        is_folder = path.endswith("/")

        parent = "/".join(path.rstrip("/").split("/")[:-1])
        parent = f"{parent}/" if parent else ""

        old_prefix = path
        new_prefix = f"{parent}{new_name}"
        if is_folder:
            new_prefix += "/"

        # DOSSIER
        if is_folder:
            objects = list(
                self.minio.list_objects(
                    bucket_name,
                    prefix=old_prefix,
                    recursive=True,
                )
            )

            if not objects:
                raise HTTPException(status_code=404, detail="Dossier introuvable")

            for obj in objects:
                if obj.object_name:
                    new_object_name = obj.object_name.replace(old_prefix, new_prefix, 1)

                    self.minio.copy_object(
                        bucket_name,
                        new_object_name,
                        CopySource(bucket_name, obj.object_name),
                    )

            delete_errors = self.minio.remove_objects(
                bucket_name,
                (DeleteObject(obj.object_name) for obj in objects if obj.object_name),
            )
            for err in delete_errors:
                raise HTTPException(
                    status_code=500,
                    detail=f"Erreur suppression objet {err}",
                )

            try:
                self.minio.remove_object(bucket_name, old_prefix)
            except Exception:
                pass

            return {"detail": "Dossier renommé avec succès"}

        # FICHIER
        try:
            self.minio.stat_object(bucket_name, path)
        except Exception:
            raise HTTPException(status_code=404, detail="Fichier introuvable")

        self.minio.copy_object(
            bucket_name,
            new_prefix,
            CopySource(bucket_name, path),
        )

        self.minio.remove_object(bucket_name, path)

        return {"detail": "Fichier renommé avec succès"}


def get_minio_service(request: Request) -> MinioService:
    """Fournit une instance de MinioService avec le client Minio de l'app."""
    return MinioService(request.app.state.minio_client)
