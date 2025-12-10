from pydantic import BaseModel
from datetime import datetime
from typing import Optional

from app.utils.response import BaseResponse


class FileMetadata(BaseModel):
    filename: Optional[str]
    size: Optional[int]
    content_type: Optional[str] = "application/octet-stream"
    upload_date: datetime
    bucket: str
    object_name: str
    url: str | None = None


class FileUploadResponse(BaseResponse[FileMetadata]):
    message: str = "File uploaded successfully"
