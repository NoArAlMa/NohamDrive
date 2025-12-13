from fastapi import APIRouter, UploadFile, Depends, status
from app.services.minio_service import MinioService, get_minio_service
from app.schemas.file_tree import SimpleFileTreeResponse, TreeResponse
from app.schemas.files import FileUploadResponse


router = APIRouter(prefix="/storage", tags=["Storage"])


@router.post(
    "/upload", response_model=FileUploadResponse, status_code=status.HTTP_201_CREATED
)
async def upload_file_endpoint(
    file: UploadFile,
    minio_service: MinioService = Depends(get_minio_service),
    user_id: int = 1,  # TODO : À remplacer par l'ID réel (via auth)
) -> FileUploadResponse:
    """
    Upload un fichier dans le bucket utilisateur.

    Args:
        file : Un fichier à uploader
        user_id : ID de l'utilisateur (injecté par l'auth)

    Returns:
        The file
    """
    metadata = await minio_service.upload_file(user_id, file)
    return FileUploadResponse(data=metadata, status_code=status.HTTP_201_CREATED)


@router.get(
    "/tree",
    response_model=TreeResponse,
    responses={
        404: {"message": "Not Found"},
        500: {"message": "Internal Server Error"},
    },
)
async def list_path(
    path: str = "", minio_service: MinioService = Depends(get_minio_service)
) -> TreeResponse:
    """
    Liste le contenu d'un chemin dans le bucket utilisateur.
    Args:
        path: Chemin relatif (ex: "dossier1/sous-dossier/"). Par défaut, liste la racine.
    Returns:
        TreeResponse: Arborescence du chemin.
    """
    bucket_name = await minio_service.ensure_bucket_exists(
        user_id=1
    )  # TODO : À adapter au système d'auth
    tree: SimpleFileTreeResponse = await minio_service.simple_list_path(
        bucket_name, path
    )

    return TreeResponse(
        success=True if tree.items else False,
        data=tree,
        status_code=status.HTTP_200_OK,
        message="Tree loaded",
    )


@router.get(
    "/download/{object_name:path}",
    responses={
        200: {
            "description": "Fichier téléchargé avec succès.",
            "content": {"application/octet-stream": {}},
        },
        404: {
            "description": "Fichier ou bucket non trouvé.",
            "content": {
                "application/json": {"example": {"detail": "Fichier non trouvé."}}
            },
        },
        500: {
            "description": "Erreur interne.",
            "content": {"application/json": {"example": {"detail": "Erreur interne."}}},
        },
    },
)
async def download_file_endpoint(
    object_name: str,
    user_id: int = 1,  # TODO: Remplacer par l'ID réel (via auth)
    minio_service: MinioService = Depends(get_minio_service),
):
    """
    Télécharge un fichier depuis le bucket utilisateur.

    ***Args:***
         **object_name** (str ): Nom du fichier à télécharger
         **user_id** : ID de l'utilisateur (injecté par l'auth)

    """
    return await minio_service.download_file(user_id, object_name)
