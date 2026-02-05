from datetime import datetime
from tempfile import SpooledTemporaryFile
import threading
import zipfile
from fastapi import HTTPException, status
from minio import Minio, S3Error
from app.services.minio.bucket_service import BucketService
from app.utils.minio_utils import MinioUtils
from app.schemas.files import ResolvePathResponse
from core.logging import setup_logger
from minio.deleteobjects import DeleteObject
import io
from minio.commonconfig import CopySource
from typing import cast, BinaryIO
import os
from concurrent.futures import ThreadPoolExecutor, as_completed

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
                length=0,
                content_type="application/x-directory",
                metadata={"last_modified": str(datetime.now().isoformat())},
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
                now = datetime.now().isoformat()

                for obj in objects:
                    if not obj.object_name:
                        continue

                    relative_path = obj.object_name[len(old_prefix) :]
                    new_object_name = new_prefix + relative_path

                    self.minio.copy_object(
                        bucket_name,
                        new_object_name,
                        CopySource(bucket_name, obj.object_name),
                        metadata={"last_modified": now}
                        if new_object_name.endswith("/")
                        else None,
                        metadata_directive="REPLACE"
                        if new_object_name.endswith("/")
                        else "COPY",
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

        source_path = MinioUtils.normalize_path(source_path, is_folder=is_folder)

        destination_folder = MinioUtils.normalize_path(
            destination_folder, is_folder=True
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
            destination_path, is_folder=is_folder
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

    async def compress_objects(
        self,
        bucket_name: str,
        object_names: list[str],
        destination_folder: str,
        output_base_name: str = "compressed_folder",
        max_workers: int = 4,
        max_zip_size_mb: int = 1024,
    ):
        """
        Compresse plusieurs objets MinIO dans une archive ZIP et l'enregistre dans le bucket.

        Args:
            bucket_name (str): Nom du bucket MinIO.
            object_names (list[str]): Liste des chemins des objets MinIO à compresser.
            output_object_name (str): Chemin de destination du fichier ZIP dans MinIO.

        Returns:
            tuple[str, dict]: Message de succès et métadonnées associées.

        Raises:
            HTTPException: En cas d'erreur lors de la lecture ou de l'écriture dans MinIO.
        """
        try:
            destination_folder = MinioUtils.normalize_path(
                destination_folder, is_folder=True
            )
            valid_objects = set()

            # Collecte des objets valides
            for obj_name in object_names:
                obj_name = MinioUtils.normalize_path(
                    obj_name, is_folder=obj_name.endswith("/")
                )
                if obj_name.endswith("/"):
                    objs = self.minio.list_objects(
                        bucket_name, prefix=obj_name, recursive=True
                    )
                    valid_objects.update(
                        o.object_name
                        for o in objs
                        if o.object_name and not o.object_name.endswith("/")
                    )
                else:
                    valid_objects.add(obj_name)

            if not valid_objects:
                raise HTTPException(400, "Aucun fichier valide à compresser.")

            output_object_name = MinioUtils.generate_available_name(
                minio_client=self.minio,
                bucket_name=bucket_name,
                base_name=output_base_name + ".zip",
                parent_path=destination_folder,
                is_folder=False,
            )

            source_prefix = (
                object_names[0]
                if len(object_names) == 1 and object_names[0].endswith("/")
                else os.path.commonpath(object_names)
                if len(object_names) > 1
                else ""
            )

            temp_zip = SpooledTemporaryFile(max_size=100 * 1024 * 1024)
            zip_lock = threading.Lock()
            total_size = 0
            max_zip_size = max_zip_size_mb * 1024 * 1024

            def add_to_zip(obj_name: str):
                nonlocal total_size
                try:
                    response = self.minio.get_object(bucket_name, obj_name)
                    arcname = (
                        obj_name[len(source_prefix) :].lstrip("/")
                        if source_prefix
                        else os.path.basename(obj_name)
                    )

                    # Création des dossiers parents
                    if "/" in arcname:
                        dirs = arcname.split("/")[:-1]
                        current_dir = ""
                        for d in dirs:
                            current_dir += d + "/"
                            with zip_lock:
                                if current_dir not in zipf.NameToInfo:
                                    zipf.writestr(current_dir, "")

                    # Ajout du fichier
                    if arcname:
                        with zip_lock:
                            with zipf.open(arcname, "w") as zip_entry:
                                for chunk in response.stream(32 * 1024):
                                    zip_entry.write(chunk)
                                    total_size += len(chunk)
                                    if total_size > max_zip_size:
                                        logger.warning(
                                            f"Taille maximale du ZIP ({max_zip_size_mb} Mo) atteinte."
                                        )
                                        return False

                    response.close()
                    response.release_conn()
                    return True

                except S3Error as e:
                    logger.error(f"Erreur MinIO pour {obj_name}: {str(e)}")
                    return False
                except Exception as e:
                    logger.error(f"Erreur inattendue pour {obj_name}: {str(e)}")
                    return False

            with zipfile.ZipFile(
                temp_zip,
                mode="w",
                compression=zipfile.ZIP_DEFLATED,
                compresslevel=6,
            ) as zipf:
                # Exécution parallèle avec verrou
                with ThreadPoolExecutor(max_workers=max_workers) as executor:
                    futures = {
                        executor.submit(add_to_zip, obj): obj for obj in valid_objects
                    }
                    success_count = 0
                    for future in as_completed(futures):
                        if future.result():
                            success_count += 1

            # Upload du ZIP
            temp_zip.seek(0)
            self.minio.put_object(
                bucket_name,
                output_object_name,
                cast(BinaryIO, temp_zip),
                length=-1,
                part_size=10 * 1024 * 1024,
                content_type="application/zip",
            )
            temp_zip.close()

            logger.info(
                f"Compression de {success_count}/{len(valid_objects)} objets vers {output_object_name} réussie."
            )
            return (
                f"Compression de {success_count} fichiers vers '{output_object_name}' réussie.",
                {
                    "objects": list(valid_objects),
                    "output_object_name": output_object_name,
                    "skipped": len(valid_objects) - success_count,
                },
            )

        except S3Error as e:
            logger.error(f"Erreur MinIO lors de la compression: {str(e)}")
            raise HTTPException(500, f"Erreur lors de la compression: {str(e)}")

    async def get_object_metadata(self, user_id: int, path: str) -> dict:
        """
        Récupère les métadonnées d'un fichier ou dossier dans MinIO.

        Args:
            user_id: ID de l'utilisateur (pour déterminer le bucket).
            path: Chemin de l'objet (ex: "dossier/fichier.txt" ou "dossier/").

        Returns:
            Dict[str, str]: Dictionnaire contenant les métadonnées.

        Raises:
            HTTPException: 404 si l'objet n'existe pas, 500 en cas d'erreur MinIO.
        """
        bucket_name = await self.bucket_service.get_user_bucket(user_id)
        path = MinioUtils.normalize_path(path, is_folder=path.endswith("/"))
        is_folder = path.endswith("/")

        try:
            if is_folder:
                # Pour un dossier, on liste les objets avec ce préfixe
                objects = list(
                    self.minio.list_objects(bucket_name, prefix=path, recursive=False)
                )
                if not objects:
                    raise HTTPException(
                        status_code=404, detail="Dossier vide ou introuvable"
                    )

                # Métadonnées "virtuelles" pour le dossier
                metadata = {
                    "nom": path.split("/")[-2],
                    "taille_octets": None,
                    "taille_ko": None,
                    "type_mime": "application/x-directory",
                    "date_modification": None,
                    "chemin": path,
                    "etag": None,
                    "version_id": None,
                    "nombre_fichiers": len(
                        list(
                            self.minio.list_objects(
                                bucket_name, prefix=path, recursive=True
                            )
                        )
                    ),
                }
            else:
                # Pour un fichier, on utilise stat_object
                stat = self.minio.stat_object(bucket_name, path)
                if stat.last_modified:
                    last_modified = datetime.fromtimestamp(
                        stat.last_modified.timestamp()
                    ).strftime("%Y-%m-%d %H:%M:%S")
                metadata = {
                    "nom": path.split("/")[-1],
                    "taille_octets": stat.size,
                    "taille_ko": round(stat.size / 1024, 2) if stat.size else None,
                    "type_mime": stat.content_type,
                    "date_modification": last_modified,
                    "chemin": path,
                    "est_dossier": False,
                    "etag": stat.etag,
                    "version_id": stat.version_id,
                }

            return metadata

        except S3Error as e:
            if e.code == "NoSuchKey":
                raise HTTPException(status_code=404, detail="Objet non trouvé")
            raise HTTPException(status_code=500, detail=f"Erreur MinIO: {str(e)}")

    async def resolve_objet(self, user_id: int, path: str):
        try:
            normalized_path = MinioUtils.normalize_path(
                path, path.endswith("/")
            ).lstrip("/")

            bucket = await self.bucket_service.get_user_bucket(user_id)

            if normalized_path == "":
                return ResolvePathResponse(
                    path="/",
                    exists=True,
                    type="directory",
                )

            dir_prefix = normalized_path.rstrip("/") + "/"
            objects = list(
                self.minio.list_objects(
                    bucket,
                    prefix=dir_prefix,
                    recursive=False,
                )
            )

            if objects:
                return ResolvePathResponse(
                    path="/" + normalized_path,
                    exists=True,
                    type="directory",
                )

            try:
                stat = self.minio.stat_object(bucket, normalized_path)
                return ResolvePathResponse(
                    path="/" + normalized_path,
                    exists=True,
                    type="file",
                    size=stat.size,
                )
            except S3Error:
                pass
            raise HTTPException(status_code=404, detail="Path does not exist")
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid path")
        except S3Error:
            raise HTTPException(status_code=500, detail="Storage error")
