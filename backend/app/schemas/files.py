from datetime import datetime

from pydantic import BaseModel
from typing import Literal, Optional, Union
from app.utils.response import BaseResponse


class BaseMetadata(BaseModel):
    name: str
    path: str
    content_type: str = "application/octet-stream"
    last_modified: Optional[datetime]


class FileMetadata(BaseMetadata):
    size_bytes: int
    size_kb: float
    etag: Optional[str]
    version_id: Optional[str]


class ImageMetadata(FileMetadata):
    width: int
    height: int
    format: str


class VideoMetadata(FileMetadata):
    width: int
    height: int
    duration: float
    codec: Optional[str]
    fps: Optional[float]


class FolderMetadata(BaseMetadata):
    file_count: int


ObjectMetadata = Union[FileMetadata, FolderMetadata]


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
