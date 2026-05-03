from datetime import datetime
from tempfile import SpooledTemporaryFile
import threading
import zipfile
from fastapi import HTTPException, status
from minio import Minio, S3Error
from app.services.minio.bucket_service import BucketService
from app.utils.minio_utils import MinioUtils
from app.schemas.files import (
    FileMetadata,
    FolderMetadata,
    ImageMetadata,
    ObjectMetadata,
    ResolvePathResponse,
    VideoMetadata,
)
from pymediainfo import MediaInfo
from core.logging import setup_logger
from minio.deleteobjects import DeleteObject
import io
from minio.commonconfig import CopySource
from typing import cast, BinaryIO, Iterable
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from core.config import settings

logger = setup_logger(__name__)


class ObjectService:
    def __init__(self, minio: Minio, bucket_service: BucketService) -> None:
        self.minio = minio
        self.bucket_service = bucket_service

    def _list_objects(self, bucket_name: str, prefix: str, recursive: bool = True):
        return list(
            self.minio.list_objects(
                bucket_name,
                prefix=prefix,
                recursive=recursive,
            )
        )

    def _prefix_exists(self, bucket_name: str, prefix: str) -> bool:
        return any(
            self.minio.list_objects(
                bucket_name,
                prefix=prefix,
                recursive=False,
            )
        )

    def _remove_objects(self, bucket_name: str, object_names: Iterable[str]) -> None:
        delete_errors = self.minio.remove_objects(
            bucket_name,
            (DeleteObject(object_name) for object_name in object_names),
        )

        for err in delete_errors:
            raise HTTPException(
                status_code=500,
                detail=f"Erreur suppression: {err.message}",
            )

    def _copy_objects(
        self,
        bucket_name: str,
        copy_pairs: list[tuple[str, str]],
        *,
        max_workers: int | None = None,
    ) -> None:
        if not copy_pairs:
            return

        max_workers = max_workers or settings.MINIO_COPY_MAX_WORKERS

        def copy_pair(pair: tuple[str, str]) -> None:
            source_name, destination_name = pair
            self.minio.copy_object(
                bucket_name,
                destination_name,
                CopySource(bucket_name, source_name),
            )

        worker_count = min(max_workers, len(copy_pairs))
        with ThreadPoolExecutor(max_workers=worker_count) as executor:
            futures = [executor.submit(copy_pair, pair) for pair in copy_pairs]
            for future in as_completed(futures):
                future.result()

    def _read_object_prefix(
        self,
        bucket_name: str,
        object_name: str,
        size: int,
    ) -> bytes:
        response = self.minio.get_object(bucket_name, object_name)
        try:
            return cast(bytes, response.read(size))
        finally:
            response.close()
            response.release_conn()

    def _read_object(self, bucket_name: str, object_name: str) -> bytes:
        response = self.minio.get_object(bucket_name, object_name)
        try:
            return cast(bytes, response.read())
        finally:
            response.close()
            response.release_conn()

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
                objects = self._list_objects(bucket_name, path)

                if not objects:
                    raise HTTPException(
                        status_code=404,
                        detail="Dossier vide ou inexistant",
                    )

                object_names = [obj.object_name for obj in objects if obj.object_name]
                self._remove_objects(bucket_name, object_names)

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
                objects = self._list_objects(bucket_name, old_prefix)
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
                copy_pairs: list[tuple[str, str]] = []

                for obj in objects:
                    if not obj.object_name:
                        continue

                    relative_path = obj.object_name[len(old_prefix) :]
                    new_object_name = new_prefix + relative_path

                    if new_object_name.endswith("/"):
                        self.minio.copy_object(
                            bucket_name,
                            new_object_name,
                            CopySource(bucket_name, obj.object_name),
                            metadata={"last_modified": now},
                            metadata_directive="REPLACE",
                        )
                    else:
                        copy_pairs.append((obj.object_name, new_object_name))

                self._copy_objects(bucket_name, copy_pairs)

                # Suppression des anciens objets
                object_names = [obj.object_name for obj in objects if obj.object_name]
                self._remove_objects(bucket_name, object_names)
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
                objects = self._list_objects(bucket_name, source_path)
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
                if self._prefix_exists(bucket_name, destination_path):
                    raise HTTPException(409, "Un dossier du même nom existe déjà.")

                # Copie récursive
                copy_pairs: list[tuple[str, str]] = []
                for obj in objects:
                    if obj.object_name:
                        relative_path = obj.object_name[len(source_path) :]
                        new_object_name = destination_path + relative_path
                        copy_pairs.append((obj.object_name, new_object_name))

                self._copy_objects(bucket_name, copy_pairs)

                # Suppression des anciens objets
                object_names = [obj.object_name for obj in objects if obj.object_name]
                self._remove_objects(bucket_name, object_names)

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
                objects = self._list_objects(bucket_name, source_path)
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
                copy_pairs: list[tuple[str, str]] = []
                for obj in objects:
                    if obj.object_name:
                        relative_path = obj.object_name[len(source_path) :]
                        new_object_name = destination_path + relative_path
                        # Vérifie que source ≠ destination
                        if obj.object_name != new_object_name:
                            copy_pairs.append((obj.object_name, new_object_name))

                self._copy_objects(bucket_name, copy_pairs)
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
        user_id: int,
        object_names: list[str],
        destination_folder: str,
        output_base_name: str = "compressed_folder",
        max_workers: int | None = None,
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
            bucket_name = await self.bucket_service.get_user_bucket(user_id)
            max_workers = max_workers or settings.MINIO_ZIP_MAX_WORKERS
            destination_folder = MinioUtils.normalize_path(
                destination_folder, is_folder=True
            )
            valid_objects: dict[str, int] = {}
            normalized_object_names: list[str] = []

            # Collecte des objets valides
            for obj_name in object_names:
                obj_name = MinioUtils.normalize_path(
                    obj_name, is_folder=obj_name.endswith("/")
                )
                normalized_object_names.append(obj_name)
                if obj_name.endswith("/"):
                    objs = self.minio.list_objects(
                        bucket_name, prefix=obj_name, recursive=True
                    )
                    for obj in objs:
                        if obj.object_name and not obj.object_name.endswith("/"):
                            valid_objects[obj.object_name] = obj.size or 0
                else:
                    try:
                        stat = self.minio.stat_object(bucket_name, obj_name)
                    except S3Error as e:
                        if e.code == "NoSuchKey":
                            continue
                        raise
                    valid_objects[obj_name] = stat.size or 0

            if not valid_objects:
                raise HTTPException(400, "Aucun fichier valide à compresser.")

            max_zip_size = max_zip_size_mb * 1024 * 1024
            total_source_size = sum(valid_objects.values())
            if total_source_size > max_zip_size:
                raise HTTPException(
                    413,
                    f"Taille maximale du ZIP ({max_zip_size_mb} Mo) dépassée.",
                )

            output_object_name = MinioUtils.generate_available_name(
                minio_client=self.minio,
                bucket_name=bucket_name,
                base_name=output_base_name + ".zip",
                parent_path=destination_folder,
                is_folder=False,
            )

            source_prefix = (
                normalized_object_names[0]
                if len(normalized_object_names) == 1
                and normalized_object_names[0].endswith("/")
                else os.path.commonpath(normalized_object_names)
                if len(normalized_object_names) > 1
                else ""
            )

            temp_zip = SpooledTemporaryFile(max_size=100 * 1024 * 1024)
            zip_lock = threading.Lock()
            total_size = 0

            def add_to_zip(obj_name: str):
                nonlocal total_size
                response = None
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
                                for chunk in response.stream(
                                    settings.MINIO_ZIP_STREAM_CHUNK_SIZE
                                ):
                                    zip_entry.write(chunk)
                                    total_size += len(chunk)
                    return True

                except S3Error as e:
                    logger.error(f"Erreur MinIO pour {obj_name}: {str(e)}")
                    return False
                except Exception as e:
                    logger.error(f"Erreur inattendue pour {obj_name}: {str(e)}")
                    return False
                finally:
                    if response is not None:
                        response.close()
                        response.release_conn()

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

    async def get_object_metadata(self, user_id: int, path: str) -> ObjectMetadata:
        try:
            bucket_name = await self.bucket_service.get_user_bucket(user_id=user_id)
            normalized_path = MinioUtils.normalize_path(
                path, is_folder=path.endswith("/")
            )
            is_dir = normalized_path.endswith("/")

            if is_dir:
                # Logique pour les dossiers (inchangée)
                folder_prefix = normalized_path.rstrip("/") + "/"
                objects = list(
                    self.minio.list_objects(
                        bucket_name, prefix=folder_prefix, recursive=True
                    )
                )
                file_count = max(len(objects) - 1, 0)
                try:
                    stat = self.minio.stat_object(bucket_name, folder_prefix)
                    last_modified = stat.last_modified
                except Exception:
                    last_modified = datetime.now()
                return FolderMetadata(
                    name=folder_prefix.rstrip("/").split("/")[-1],
                    path="/" + folder_prefix,
                    content_type="application/x-directory",
                    last_modified=last_modified,
                    file_count=file_count,
                )

            stat = self.minio.stat_object(bucket_name, normalized_path)
            last_modified = stat.last_modified
            mime_type = MinioUtils.detect_mime(normalized_path, stat.content_type)
            content_type = MinioUtils.get_file_type(normalized_path, mime_type)

            base_metadata = {
                "name": normalized_path.split("/")[-1],
                "path": "/" + normalized_path,
                "content_type": content_type,
                "last_modified": last_modified,
                "size_bytes": stat.size or 0,
                "size_kb": round((stat.size or 0) / 1024, 2),
                "etag": stat.etag,
                "version_id": stat.version_id,
            }

            if content_type == "image":
                data = self._read_object_prefix(
                    bucket_name,
                    normalized_path,
                    settings.MINIO_IMAGE_METADATA_READ_SIZE,
                )
                try:
                    img_meta = MinioUtils.extract_image_metadata(data)
                except Exception:
                    data = self._read_object(bucket_name, normalized_path)
                    img_meta = MinioUtils.extract_image_metadata(data)
                return ImageMetadata(**base_metadata, **img_meta)

            elif content_type == "video":
                video_data = self._read_object(bucket_name, normalized_path)
                media_info_json = MediaInfo.parse(io.BytesIO(video_data), output="JSON")
                video_meta = MinioUtils.extract_video_metadata(media_info_json)
                logger.info(video_meta)
                return VideoMetadata(**base_metadata, **video_meta)

            else:
                return FileMetadata(**base_metadata)

        except S3Error as e:
            logger.error(f"Erreur récupération metadata {path}: {e}")
            raise HTTPException(
                status_code=404 if e.code == "NoSuchKey" else 500,
                detail=f"Impossible de récupérer les métadonnées: {str(e)}",
            )

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

            if self._prefix_exists(bucket, dir_prefix):
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
