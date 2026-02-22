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

    path: str
    items: List[SimpleFileItem]
    total_pages: int
    total_items: int
    per_page: int
    page: int


class FullFileItem(BaseModel):
    """Représente un fichier ou dossier avec toutes ses métadonnées."""

    name: str
    is_dir: bool
    size: Optional[int]
    last_modified: datetime
    etag: Optional[str]
    content_type: Optional[str]

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()  # Sérialisation ISO pour les timestamps
        }


class FullFileTreeResponse(BaseModel):
    """Réponse complète pour l'arborescence avec métadonnées."""

    path: str
    items: list[FullFileItem]
    total_items: int

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}
