from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class FileMetadata(BaseModel):
    filename: str
    size: int
    content_type: str
    upload_date: datetime
    bucket: str
    object_name: str
    url: str | None = None


class FileUpload(BaseModel):
    """Schéma pour la réponse après upload."""

    filename: str
    size: int
    content_type: str
    upload_date: datetime
    bucket: str
    object_name: str
    url: Optional[str] = None
    status: str = "success"
