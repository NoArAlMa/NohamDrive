from fastapi import APIRouter, UploadFile, Depends
from app.services.minio_service import FileService, get_file_service
from datetime import datetime
from app.schemas.files import FileUpload
from core.minio_client import get_healthy_minio


router = APIRouter(prefix="/storage", tags=["Storage"])


@router.post("/upload", response_model=FileUpload)
async def upload_file_endpoint(
    file: UploadFile,
    file_service: FileService = Depends(get_file_service),
    user_id: int = 1,  # À remplacer par l'ID réel (via auth)
):
    """
    Upload un fichier dans le bucket utilisateur.
    """
    metadata = await file_service.upload_file(user_id, file)
    return FileUpload(**metadata.model_dump(), status="success")


@router.get("/health")
async def health_check(minio_status: dict = Depends(get_healthy_minio)):
    return {
        "status": "ok",
        "timestamp": datetime.now().isoformat(),
    }
