from fastapi import HTTPException, status
from minio import Minio, S3Error
from app.services.minio.bucket_service import BucketService
from app.utils.minio_utils import MinioUtils
from core.logging import setup_logger
from minio.deleteobjects import DeleteObject
import io
from minio.commonconfig import CopySource

logger = setup_logger(__name__)


class ObjectService:
    def __init__(self, minio: Minio, bucket_service: BucketService) -> None:
        self.minio = minio
        self.bucket_service = bucket_service

    async def delete_object(self, user_id: int, path: str) -> tuple:
        """
        Supprime un fichier ou un dossier (récursif) dans MinIO.

        - Fichier : "docs/file.txt"
        - Dossier : "docs/folder/"
        """

        bucket_name = await self.bucket_service.get_user_bucket(user_id)

   
        # Normalisation & sécurité
        is_folder = path.endswith("/")
        path = MinioUtils.normalize_path(path, is_folder=is_folder)


        # Suppression dossier
        try:
            if is_folder:
                objects = list(
                    self.minio.list_objects(
                        bucket_name,
                        prefix=path,
                        recursive=True,
                    )
                )

                if not objects:
                    raise HTTPException(
                        status_code=404,
                        detail="Dossier vide ou inexistant",
                    )

                delete_errors = self.minio.remove_objects(
                    bucket_name,
                    (
                        DeleteObject(obj.object_name)
                        for obj in objects
                        if obj.object_name
                    ),
                )

                for err in delete_errors:
                    raise HTTPException(
                        status_code=500,
                        detail=f"Erreur suppression: {err.message}",
                    )

                return (
                    f"Dossier '{path}' supprimé ({len(objects)} objets)",
                    {
                        "path": path,
                    },
                )

            # Suppression fichier

            else:
                try:
                    self.minio.stat_object(bucket_name, path)
                except S3Error as e:
                    if e.code == "NoSuchKey":
                        raise HTTPException(
                            status_code=404,
                            detail="Fichier non trouvé",
                        )
                    raise

                self.minio.remove_object(bucket_name, path)

                return (f"Fichier '{path}' supprimé avec succès", {"path": path})

        except S3Error as e:
            raise HTTPException(
                status_code=500,
                detail=f"Erreur lors de la suppression : {str(e)}",
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
        bucket_name = await self.bucket_service.get_user_bucket(user_id)

        # Nettoie et normalise le chemin
        current_path_normalized = MinioUtils.normalize_path(
            current_path, is_folder=True
        )
        folder_path_normalized = MinioUtils.normalize_path(folder_path, is_folder=True)
        full_path = f"{current_path_normalized.rstrip('/')}/{folder_path_normalized.strip('/')}/"

        logger.info(f"Chemin complet du dossier à créer: {full_path}")

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
                io.BytesIO(b""),
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

    async def rename(self, user_id: int, path: str, new_name: str) -> tuple:
        bucket_name = await self.bucket_service.get_user_bucket(user_id)

        # Validation & normalisation
        path = MinioUtils.normalize_path(path, is_folder=path.endswith("/"))
        new_name = MinioUtils.sanitize_name(new_name)

        is_folder = path.endswith("/")
        old_prefix = path

        # Détection du parent
        parent_path = MinioUtils.get_parent_path(path)

        # Génération du nouveau nom disponible
        new_prefix = MinioUtils.generate_available_name(
            minio_client=self.minio,
            bucket_name=bucket_name,
            base_name=new_name,
            parent_path=parent_path,
            is_folder=is_folder,
        )

        if is_folder:
            new_prefix = MinioUtils.normalize_path(new_prefix, is_folder=True)

        # Récupération et vérification

        try:
            if is_folder:
                objects = list(
                    self.minio.list_objects(
                        bucket_name, prefix=old_prefix, recursive=True
                    )
                )
                if not objects:
                    raise HTTPException(status_code=404, detail="Dossier introuvable")
            else:
                self.minio.stat_object(bucket_name, path)
        except S3Error as e:
            if e.code == "NoSuchKey":
                raise HTTPException(status_code=404, detail="Objet introuvable")
            raise HTTPException(status_code=500, detail=f"Erreur MinIO: {str(e)}")

        # Renommage

        try:
            if is_folder:
                # Copie récursive
                for obj in objects:
                    if obj.object_name:
                        relative_path = obj.object_name[len(old_prefix) :]
                        new_object_name = new_prefix + relative_path
                        self.minio.copy_object(
                            bucket_name,
                            new_object_name,
                            CopySource(bucket_name, obj.object_name),
                        )

                # Suppression des anciens objets
                delete_errors = self.minio.remove_objects(
                    bucket_name,
                    (
                        DeleteObject(obj.object_name)
                        for obj in objects
                        if obj.object_name
                    ),
                )
                for err in delete_errors:
                    raise HTTPException(
                        status_code=500, detail=f"Erreur suppression objet {err}"
                    )
            else:
                # Fichier unique
                self.minio.copy_object(
                    bucket_name,
                    new_prefix,
                    CopySource(bucket_name, path),
                )
                self.minio.remove_object(bucket_name, path)

            return (
                f"{'Dossier' if is_folder else 'Fichier'} renommé avec succès : {new_prefix}",
                {"old_prefix": old_prefix, "new_prefix": new_prefix},
            )

        except S3Error as e:
            raise HTTPException(
                status_code=500, detail=f"Erreur lors du renommage: {str(e)}"
            )

    async def move(
        self,
        user_id: int,
        source_path: str,
        destination_folder: str,
    ) -> tuple:
        """
        Déplace un fichier ou un dossier dans MinIO.

        Args:
            user_id: ID de l'utilisateur.
            source_path: Chemin source (ex: "dossier1/fichier.txt" ou "dossier1/").
            destination_folder: Chemin du dossier de destination (ex: "dossier2/").
            is_folder: Si True, traite le source_path comme un dossier.

        Returns:
            tuple: Message de succès, data.

        Raises:
            HTTPException: 400 si chemin invalide, 404 si source introuvable, 500 en cas d'erreur.
        """
        bucket_name = await self.bucket_service.get_user_bucket(user_id)

        source_path = MinioUtils.normalize_path(
            source_path, is_folder=source_path.endswith("/")
        )

        destination_folder = MinioUtils.normalize_path(
            destination_folder, is_folder=True
        )

        is_folder = source_path.endswith("/")

        # Détection du nom de base
        clean_source = source_path.rstrip("/")
        base_name = clean_source.split("/")[-1]

        # Chemin parent source
        source_parent = MinioUtils.get_parent_path(source_path)

        # Interdiction de déplacer dans le même dossier
        if source_parent == destination_folder:
            raise HTTPException(
                status_code=409,
                detail="Impossible de déplacer un élément dans le même dossier.",
            )

        # Génération du chemin destination (gestion des doublons)
        destination_path = MinioUtils.generate_available_name(
            minio_client=self.minio,
            bucket_name=bucket_name,
            base_name=base_name,
            parent_path=destination_folder,
            is_folder=is_folder,
        )

        # Sécurité finale pour les dossiers
        destination_path = MinioUtils.normalize_path(
            destination_path, is_folder=is_folder
        )
        # Vérification existence source
        try:
            if is_folder:
                objects = list(
                    self.minio.list_objects(
                        bucket_name,
                        prefix=source_path,
                        recursive=True,
                    )
                )
                if not objects:
                    raise HTTPException(404, "Dossier introuvable ou vide.")
            else:
                self.minio.stat_object(bucket_name, source_path)

        except S3Error as e:
            if e.code == "NoSuchKey":
                raise HTTPException(404, "Source introuvable.")
            raise HTTPException(500, f"Erreur MinIO: {str(e)}")

        # Déplacement
        try:
            if is_folder:
                # Vérifie collision dossier
                existing = list(
                    self.minio.list_objects(
                        bucket_name,
                        prefix=destination_path,
                        recursive=True,
                    )
                )
                if existing:
                    raise HTTPException(409, "Un dossier du même nom existe déjà.")

                # Copie récursive
                for obj in objects:
                    if obj.object_name:
                        relative_path = obj.object_name[len(source_path) :]
                        new_object_name = destination_path + relative_path

                        self.minio.copy_object(
                            bucket_name,
                            new_object_name,
                            CopySource(bucket_name, obj.object_name),
                        )

                # Suppression des anciens objets
                delete_errors = self.minio.remove_objects(
                    bucket_name,
                    (
                        DeleteObject(obj.object_name)
                        for obj in objects
                        if obj.object_name
                    ),
                )

                for err in delete_errors:
                    raise HTTPException(
                        500,
                        f"Erreur suppression: {err.message}",
                    )

            else:
                # Vérifie collision fichier
                try:
                    self.minio.stat_object(bucket_name, destination_path)
                    raise HTTPException(
                        409,
                        "Un fichier du même nom existe déjà.",
                    )
                except S3Error as e:
                    if e.code != "NoSuchKey":
                        raise

                self.minio.copy_object(
                    bucket_name,
                    destination_path,
                    CopySource(bucket_name, source_path),
                )

                self.minio.remove_object(bucket_name, source_path)
            logger.info(f"Déplacement de {source_path} vers {destination_path} réussi.")
            return (
                f"Déplacement de '{source_path}' vers '{destination_path}' réussi.",
                {"source_path": source_path, "destination_path": destination_path},
            )

        except S3Error as e:
            raise HTTPException(
                500,
                f"Erreur lors du déplacement: {str(e)}",
            )

    async def copy(
        self,
        user_id: int,
        source_path: str,
        destination_folder: str,
    ) -> tuple:
        """
        Copie un fichier ou un dossier dans MinIO.
        """
        bucket_name = await self.bucket_service.get_user_bucket(user_id)

        is_folder = source_path.endswith("/")

        source_path = MinioUtils.normalize_path(
            source_path,
            is_folder=is_folder
        )

        destination_folder = MinioUtils.normalize_path(
            destination_folder,
            is_folder=True
        )

        # Détection du nom de base
        clean_source = source_path.rstrip("/")
        base_name = clean_source.split("/")[-1]

        # Génération du chemin de destination (gestion des doublons)
        destination_path = MinioUtils.generate_available_name(
            minio_client=self.minio,
            bucket_name=bucket_name,
            base_name=base_name,
            parent_path=destination_folder,
            is_folder=is_folder,
        )

        # Sécurité finale (important pour les dossiers)
        destination_path = MinioUtils.normalize_path(
            destination_path,
            is_folder=is_folder
        )
        # Vérification de l'existence de la source
        try:
            if is_folder:
                objects = list(
                    self.minio.list_objects(
                        bucket_name,
                        prefix=source_path,
                        recursive=True,
                    )
                )
                if not objects:
                    raise HTTPException(404, "Dossier introuvable ou vide.")
            else:
                self.minio.stat_object(bucket_name, source_path)

        except S3Error as e:
            if e.code == "NoSuchKey":
                raise HTTPException(404, "Source introuvable.")
            raise HTTPException(500, f"Erreur MinIO: {str(e)}")

        # Copie
        try:
            if is_folder:
                for obj in objects:
                    if obj.object_name:
                        relative_path = obj.object_name[len(source_path) :]
                        new_object_name = destination_path + relative_path
                        # Vérifie que source ≠ destination
                        if obj.object_name != new_object_name:
                            self.minio.copy_object(
                                bucket_name,
                                new_object_name,
                                CopySource(bucket_name, obj.object_name),
                            )
            else:
                # Vérifie que source ≠ destination
                if source_path != destination_path:
                    self.minio.copy_object(
                        bucket_name,
                        destination_path,
                        CopySource(bucket_name, source_path),
                    )
                else:
                    raise HTTPException(
                        400,
                        "Impossible de copier un objet sur lui-même sans modification.",
                    )

            logger.info(f"Copie de {source_path} vers {destination_path} réussie.")
            return (
                f"Copie de '{source_path}' vers '{destination_path}' réussie.",
                {
                    "source_path": source_path,
                    "destination_path": destination_path,
                },
            )

        except S3Error as e:
            raise HTTPException(500, f"Erreur lors de la copie: {str(e)}")
