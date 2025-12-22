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
import zipfile

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

    async def delete_object(self, user_id: int, path: str) -> tuple:
        """
        Supprime un fichier ou un dossier (récursif) dans MinIO.

        - Fichier : "docs/file.txt"
        - Dossier : "docs/folder/"
        """

        bucket_name = await self.get_user_bucket(user_id)

        # Sécurité & normalisation

        if ".." in path:
            raise HTTPException(status_code=400, detail="Chemin invalide.")

        is_folder = path.endswith("/")

        path = path.strip("/")

        if is_folder:
            path = path.rstrip("/") + "/"

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

    async def download_object(
        self, user_id: int, object_name: str
    ) -> StreamingResponse:
        """
        Télécharge un fichier ou un dossier depuis MinIO.

        - Si `object_name` est un fichier → streaming direct.
        - Si `object_name` est un dossier → compression ZIP et streaming.

        Args:
            user_id: ID de l'utilisateur (détermine le bucket).
            object_name: Nom de l'objet ou préfixe de dossier.

        Returns:
            StreamingResponse: Flux du fichier ou ZIP à télécharger.

        Raises:
            HTTPException: 404 si le fichier ou le bucket n'existe pas,
                        400 si chemin invalide,
                        500 en cas d'erreur interne.
        """
        bucket_name = await self.get_user_bucket(user_id)

        # Vérifie le chemin
        if ".." in object_name or object_name.startswith("/"):
            raise HTTPException(status_code=400, detail="Chemin invalide.")

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

            # Si c'est un fichier, on stream directement
            if is_file:
                file_stream = self.minio.get_object(bucket_name, object_name)
                return StreamingResponse(
                    content=file_stream.stream(amt=1024 * 1024),  # chunks de 1 Mo
                    media_type=obj.content_type or "application/octet-stream",
                    headers={
                        "Content-Disposition": f"attachment; filename={object_name.split('/')[-1]}",
                        "Content-Length": str(obj.size),
                    },
                )

            # On normalise le prefix pour lister les objets, mais on garde object_name pour le nom du ZIP
            prefix = object_name.rstrip("/") + "/"

            objects = list(
                self.minio.list_objects(bucket_name, prefix=prefix, recursive=True)
            )
            if not objects:
                raise HTTPException(
                    status_code=404,
                    detail=f"Objet ou dossier {object_name} introuvable.",
                )

            # Création du ZIP en mémoire
            zip_buffer = io.BytesIO()
            with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zipf:
                for obj in objects:
                    if not obj.object_name or obj.object_name.endswith("/"):
                        continue  # ignore les "dossiers" vides
                    data = self.minio.get_object(bucket_name, obj.object_name)
                    file_bytes = data.read()
                    # Chemin relatif correct
                    relative_name = obj.object_name[len(prefix) :]
                    zipf.writestr(relative_name, file_bytes)

            zip_buffer.seek(0)

            return StreamingResponse(
                zip_buffer,
                media_type="application/zip",
                headers={
                    "Content-Disposition": f"attachment; filename={object_name.split('/')[-1]}.zip"
                },
            )

        except S3Error as e:
            logger.error(
                "Échec du téléchargement",
                extra={"user_id": user_id, "object_name": object_name, "error": str(e)},
            )
            raise HTTPException(
                status_code=500,
                detail=f"Erreur lors du téléchargement: {str(e)}",
            )

    async def rename(self, user_id: int, path: str, new_name: str) -> tuple:
        bucket_name = await self.get_user_bucket(user_id)

        # Validation & normalisation
        if ".." in path or ".." in new_name or "/" in new_name:
            raise HTTPException(status_code=400, detail="Chemin invalide")

        path = path.lstrip("/")
        is_folder = path.endswith("/")

        parent = "/".join(path.rstrip("/").split("/")[:-1])
        parent = f"{parent}/" if parent else ""

        old_prefix = path

        # Génération du nouveau nom disponible

        new_prefix = self._generate_available_name(
            bucket_name=bucket_name,
            base_name=new_name,
            parent_path=parent,
            is_folder=is_folder,
        )

        if is_folder:
            new_prefix = new_prefix.rstrip("/") + "/"

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
        bucket_name = await self.get_user_bucket(user_id)

        # Normalisation des chemins
        def normalize_folder(path: str) -> str:
            return path.strip("/").rstrip("/") + "/"

        if ".." in source_path or ".." in destination_folder:
            raise HTTPException(400, "Chemin invalide.")

        is_folder = source_path.endswith("/")

        source_path = source_path.strip("/")
        if is_folder:
            source_path += "/"

        destination_folder = normalize_folder(destination_folder)

        # Détection nom de base
        clean_source = source_path.rstrip("/")
        base_name = clean_source.split("/")[-1]

        source_parent = (
            "/".join(clean_source.split("/")[:-1]) + "/" if "/" in clean_source else ""
        )

        if normalize_folder(source_parent) == destination_folder:
            raise HTTPException(
                409, "Impossible de déplacer un élément dans le même dossier."
            )

        # Génération chemin destination
        destination_path = self._generate_available_name(
            bucket_name=bucket_name,
            base_name=base_name,
            parent_path=destination_folder,
            is_folder=is_folder,
        )

        if is_folder:
            destination_path = destination_path.rstrip("/") + "/"

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
        bucket_name = await self.get_user_bucket(user_id)

        # Normalisation des chemins
        if ".." in source_path or ".." in destination_folder:
            raise HTTPException(400, "Chemin invalide.")

        is_folder = source_path.endswith("/")
        source_path = source_path.strip("/")
        if is_folder:
            source_path += "/"

        destination_folder = destination_folder.strip("/")

        if destination_folder:
            destination_folder += "/"

        # Détection du nom de base
        clean_source = source_path.rstrip("/")
        base_name = clean_source.split("/")[-1]

        # Génération du chemin de destination (avec gestion des doublons)
        destination_path = self._generate_available_name(
            bucket_name=bucket_name,
            base_name=base_name,
            parent_path=destination_folder,
            is_folder=is_folder,
        )

        if is_folder:
            destination_path = destination_path.rstrip("/") + "/"

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

    def _generate_available_name(
        self,
        bucket_name: str,
        base_name: str,
        parent_path: str,
        is_folder: bool,
    ) -> str:
        """
        Génère un nom disponible façon Windows :
        file.txt → file (1).txt
        folder/ → folder (1)/
        """
        # Normalisation du parent path : "" pour racine, sinon "dossier/"
        parent_path = parent_path.strip("/")
        if parent_path:
            parent_path += "/"

        # Séparation nom / extension pour fichiers
        if is_folder:
            name = base_name.rstrip("/")
            ext = ""
        else:
            # Cas spécial fichiers commençant par un point, ex: ".env" ce fdp
            if "." in base_name and not base_name.startswith("."):
                name, ext = base_name.rsplit(".", 1)
                ext = "." + ext
            else:
                name = base_name
                ext = ""

        index = 0
        while True:
            suffix = f" ({index})" if index > 0 else ""
            candidate = f"{parent_path}{name}{suffix}{ext}"
            if is_folder:
                candidate += "/"

            # Vérifie si le candidate existe
            exists = False
            if is_folder:
                objs = list(
                    self.minio.list_objects(
                        bucket_name, prefix=candidate, recursive=True
                    )
                )
                exists = len(objs) > 0
            else:
                try:
                    self.minio.stat_object(bucket_name, candidate)
                    exists = True
                except S3Error as e:
                    if e.code == "NoSuchKey":
                        exists = False
                    else:
                        raise

            # S'assure que candidate n'est pas identique à la source
            if not exists:
                return candidate

            index += 1


def get_minio_service(request: Request) -> MinioService:
    """Fournit une instance de MinioService avec le client Minio de l'app."""
    return MinioService(request.app.state.minio_client)
