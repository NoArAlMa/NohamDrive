import re
from fastapi import HTTPException
from minio import Minio

WINDOWS_SUFFIX_RE = re.compile(r"^(.*?)(?: \((\d+)\))?$")


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
        Nettoie un nom de fichier ou dossier en :
        - Gardant les accents et les espaces.
        - Remplaçant les caractères interdits par un underscore.
        """

        if len(name) > 30:
            raise HTTPException(
                status_code=400, detail="Nom trop long (+30 caractères)"
            )

        if not name or "/" in name or ".." in name:
            raise HTTPException(status_code=400, detail="Nom invalide")

        # Caractères interdits dans les noms de fichiers
        forbidden_chars = r'[\\/*?:"<>|]'
        # Remplace les caractères interdits par un underscore
        name = re.sub(forbidden_chars, "_", name)

        return name

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
        parent_path = parent_path.strip("/")
        if parent_path:
            parent_path += "/"

        # --- Séparation nom / extension ---
        if is_folder:
            raw_name = base_name.rstrip("/")
            ext = ""
        else:
            if "." in base_name and not base_name.startswith("."):
                raw_name, ext = base_name.rsplit(".", 1)
                ext = "." + ext
            else:
                raw_name = base_name
                ext = ""

        # --- Extraction du vrai nom + suffixe éventuel ---
        match = WINDOWS_SUFFIX_RE.match(raw_name)
        if match:
            base_clean_name = match.group(1)

        # --- Liste tous les objets concurrents ---
        prefix = f"{parent_path}{base_clean_name}"
        existing_indexes = set()

        objs = minio_client.list_objects(bucket_name, prefix=prefix, recursive=False)

        for obj in objs:
            name = obj.object_name

            if name and not name.startswith(parent_path):
                continue

            filename = name[len(parent_path) :] if name else ""

            if is_folder:
                filename = filename.rstrip("/")
            else:
                if not filename.endswith(ext):
                    continue
                filename = filename[: -len(ext)]

            m = WINDOWS_SUFFIX_RE.match(filename)
            if m and m.group(1) == base_clean_name:
                idx = int(m.group(2)) if m.group(2) else 0
                existing_indexes.add(idx)

        # --- Trouve le premier index libre ---
        index = 0
        while index in existing_indexes:
            index += 1

        suffix = f" ({index})" if index > 0 else ""
        candidate = f"{parent_path}{base_clean_name}{suffix}{ext}"

        if is_folder:
            candidate += "/"

        return candidate
