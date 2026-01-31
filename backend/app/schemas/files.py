from pydantic import BaseModel
from datetime import datetime
from typing import Literal, Optional
from app.utils.response import BaseResponse


class FileMetadata(BaseModel):
    filename: Optional[str]
    size: Optional[int]
    content_type: Optional[str] = "application/octet-stream"
    upload_date: datetime
    bucket: str
    object_name: str
    url: str | None = None


class CreateFolder(BaseModel):
    currentPath: str
    folderPath: str


class CopyItem(BaseModel):
    source_path: str
    destination_folder: str


class RenameItem(BaseModel):
    path: str
    new_name: str


class MoveItem(BaseModel):
    source_path: str
    destination_folder: str


class CompressItems(BaseModel):
    objects: list[str]
    destination_folder: str


class ResolvePathResponse(BaseModel):
    path: str
    exists: bool
    type: Literal["file", "directory"]
    size: Optional[int] = None


class FileUploadResponse(BaseResponse[FileMetadata]):
    message: str = "File uploaded successfully"
