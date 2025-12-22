import re
from fastapi import HTTPException
from minio import Minio, S3Error


class MinioUtils:
    @staticmethod
    def get_parent_path(path: str) -> str:
        """
        Retourne le dossier parent d’un path
        ex: dossier1/dossier2/file.txt → dossier1/dossier2/
        """
        parts = path.rstrip("/").split("/")
        if len(parts) <= 1:
            return ""
        return "/".join(parts[:-1]) + "/"

    @staticmethod
    def sanitize_name(name: str) -> str:
        """
        Nettoie un nom de fichier ou dossier
        """
        if not name or "/" in name or ".." in name:
            raise HTTPException(status_code=400, detail="Nom invalide")

        return re.sub(r"[^a-zA-Z0-9_.()-]", "_", name)

    @staticmethod
    def normalize_path(path: str, is_folder: bool = False) -> str:
        """
        Nettoie et normalise un chemin MinIO.
        - Supprime les / en début et fin
        - Interdit les .. pour éviter l'accès non autorisé
        - Ajoute / à la fin si dossier
        """
        p = path.strip("/")
        if ".." in p:
            raise HTTPException(status_code=400, detail="Chemin invalide")
        if is_folder and not p.endswith("/"):
            p += "/"
        return p

    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """
        Nettoie un nom de fichier pour enlever les caractères invalides
        """
        if not filename:
            raise HTTPException(status_code=400, detail="Nom de fichier vide")
        base, ext = filename.rsplit(".", 1) if "." in filename else (filename, "")
        base = re.sub(r"[^a-zA-Z0-9_.-]", "_", base)
        ext = f".{ext}" if ext else ""
        return base + ext

    @staticmethod
    def generate_available_name(
        minio_client: Minio,
        bucket_name: str,
        base_name: str,
        parent_path: str = "",
        is_folder: bool = False,
    ) -> str:
        """
        Génère un nom disponible façon Windows:
        file.txt -> file (1).txt
        folder/ -> folder (1)/
        """
        parent_path = parent_path.strip("/")
        if parent_path:
            parent_path += "/"

        if is_folder:
            name = base_name.rstrip("/")
            ext = ""
        else:
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

            exists = False
            if is_folder:
                objs = list(
                    minio_client.list_objects(
                        bucket_name, prefix=candidate, recursive=True
                    )
                )
                exists = len(objs) > 0
            else:
                try:
                    minio_client.stat_object(bucket_name, candidate)
                    exists = True
                except S3Error as e:
                    if e.code == "NoSuchKey":
                        exists = False
                    else:
                        raise

            if not exists:
                return candidate
            index += 1
