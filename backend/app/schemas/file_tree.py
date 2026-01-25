# backend/schemas/file_tree.py
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


class SimpleFileItem(BaseModel):
    """Un objet MinIO brut, sans traitement complexe."""

    name: Optional[str]  # Nom de l'objet (ex: "dossier/fichier.txt")
    size: Optional[int]  # Taille en octets
    is_dir: bool  # True si c'est un "dossier" (préfixe), False si c'est un fichier
    last_modified: datetime


class SimpleFileTreeResponse(BaseModel):
    """Réponse minimaliste pour lister les objets."""

    path: str  # Chemin actuel (ex: "mon-dossier/")
    items: List[SimpleFileItem]  # Liste des objets
    total_pages: int
    total_items: int
    per_page: int
    page: int