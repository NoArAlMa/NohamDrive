from typing import List
from fastapi import HTTPException, status

from minio import Minio, S3Error
from minio.deleteobjects import DeleteObject
from core.logging import setup_logger


logger = setup_logger(__name__)


class BucketService:
    def __init__(self, minio: Minio) -> None:
        self.minio = minio

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

    async def delete_user_bucket(self, user_id: int) -> None:
        """
        Supprime définitivement et intégralement le bucket d'un utilisateur.
        """

        bucket_name = await self.get_user_bucket(user_id)

        try:
            # 1️⃣ Vérification existence bucket
            if not self.minio.bucket_exists(bucket_name):
                logger.warning(f"[DELETE_BUCKET] Bucket {bucket_name} inexistant.")
                return

            logger.info(f"[DELETE_BUCKET] Suppression du bucket {bucket_name}...")

            # 2️⃣ Récupération de tous les objets
            objects = self.minio.list_objects(bucket_name, recursive=True)

            delete_objects: List[DeleteObject] = [
                DeleteObject(obj.object_name) for obj in objects if obj.object_name
            ]

            # 3️⃣ Suppression batch (gros buckets supportés)
            if delete_objects:
                errors = self.minio.remove_objects(bucket_name, delete_objects)

                deletion_errors = list(errors)
                if deletion_errors:
                    for error in deletion_errors:
                        logger.error(
                            f"[DELETE_BUCKET] Erreur suppression objet: {error}"
                        )

                    raise HTTPException(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail="Erreur lors de la suppression complète du stockage utilisateur.",
                    )

            # 4️⃣ Suppression finale du bucket (vide)
            self.minio.remove_bucket(bucket_name)

            logger.info(
                f"[DELETE_BUCKET] Bucket {bucket_name} supprimé définitivement pour user {user_id}."
            )

        except S3Error as e:
            logger.error(
                f"[DELETE_BUCKET] Erreur MinIO pour {bucket_name}: {e.code} - {e.message}"
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erreur stockage lors de la suppression du compte.",
            )

        except Exception as e:
            logger.exception(
                f"[DELETE_BUCKET] Erreur inattendue suppression bucket {bucket_name}: {e}"
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erreur serveur lors de la suppression du stockage.",
            )

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
