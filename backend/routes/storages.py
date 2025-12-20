from fastapi import APIRouter, HTTPException, UploadFile, Depends, status, Query
from app.services.minio_service import MinioService, get_minio_service
from app.schemas.file_tree import SimpleFileTreeResponse, TreeResponse
from app.schemas.files import CreateFolder, FileUploadResponse
from app.utils.response import BaseResponse


router = APIRouter(prefix="/storage", tags=["Storage"])


@router.post(
    "/upload", response_model=FileUploadResponse, status_code=status.HTTP_201_CREATED
)
async def upload_file_endpoint(
    file: UploadFile,
    minio_service: MinioService = Depends(get_minio_service),
    user_id: int = 1,  # TODO : À remplacer par l'ID réel (via auth)
    path: str = "",
) -> FileUploadResponse:
    """
    Upload un fichier dans le bucket utilisateur.

    Args:
        file : Un fichier à uploader
        user_id : ID de l'utilisateur (injecté par l'auth)

    Returns:
        Le fichier à télécharger
    """

    if not file.filename:
        raise HTTPException(status_code=400, detail="Nom de fichier vide.")

    try:
        metadata = await minio_service.upload_file(user_id, file, path)
        return FileUploadResponse(data=metadata, status_code=status.HTTP_201_CREATED)
    except HTTPException as e:
        # Log côté endpoint si nécessaire
        # logger.error(f"Erreur upload user {user_id}, fichier {file.filename}: {e.detail}")
        raise e


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


@router.post(
    "/folder",
    response_model=BaseResponse[str],
    status_code=status.HTTP_201_CREATED,
    responses={
        201: {
            "description": "Dossier créé avec succès.",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "data": "dossier_parent/nouveau_dossier/",
                        "message": "Dossier créé avec succès.",
                    }
                }
            },
        },
        400: {
            "description": "Requête invalide (chemin ou dossier existant).",
            "content": {
                "application/json": {
                    "example": {
                        "success": False,
                        "data": None,
                        "message": "Le dossier 'dossier/' existe déjà.",
                    }
                }
            },
        },
        500: {
            "description": "Erreur interne.",
            "content": {
                "application/json": {
                    "example": {
                        "success": False,
                        "data": None,
                        "message": "Impossible de créer le dossier.",
                    }
                }
            },
        },
    },
)
async def create_folder_endpoint(
    request: CreateFolder,
    user_id: int = 1,  # ID de l'utilisateur (via auth),
    minio_service: MinioService = Depends(get_minio_service),
) -> BaseResponse[str]:
    """
    Crée un dossier dans le bucket utilisateur.

    **Args:**
        - **request (CreateFolder):** Objet contenant:
            - `currentPath (str)`: Chemin parent (ex: "dossier_parent/").
            - `folderPath (str)`: Nom du nouveau dossier (ex: "nouveau_dossier").
        - **user_id (int):** ID de l'utilisateur (injecté par l'auth).

    **Returns:**
        - **BaseResponse**: Réponse standard avec:
            - `success (bool)`: Statut de la requête.
            - `data (str)`: Chemin complet du dossier créé.
            - `message (str)`: Message de confirmation ou d'erreur.


    """
    try:
        folder_path = await minio_service.create_folder(
            user_id=user_id,
            current_path=request.currentPath,
            folder_path=request.folderPath,
        )
        return BaseResponse(
            success=True,
            data=folder_path,
            message="Dossier créé avec succès.",
        )
    except HTTPException as e:
        raise e


@router.delete(
    "/file",
    response_model=BaseResponse,
    status_code=status.HTTP_200_OK,
    responses={
        200: {"description": "Fichier supprimé avec succès"},
        404: {"description": "Fichier inexistant"},
        500: {"description": "Erreur interne"},
    },
)
async def delete_file_endpoint(
    object_name: str = Query(..., description="Nom du fichier à supprimer"),
    minio_service: MinioService = Depends(get_minio_service),
    user_id: int = 1,
):
    await minio_service.delete_file(user_id, object_name)

    return BaseResponse(
        success=True,
        data=None,
        message="Fichier supprimé avec succès",
        status_code=status.HTTP_200_OK,
    )


@router.delete(
    "/folder",
    response_model=BaseResponse,
    status_code=status.HTTP_200_OK,
    responses={
        200: {"description": "Dossier supprimé avec succès"},
        404: {"description": "Dossier inexistant"},
        500: {"description": "Erreur interne"},
    },
)
async def delete_folder_endpoint(
    folder_path: str = Query(..., description="Chemin du dossier à supprimer"),
    minio_service: MinioService = Depends(get_minio_service),
    user_id: int = 1,
):
    await minio_service.delete_folder(user_id, folder_path)

    return BaseResponse(
        success=True,
        data=None,
        message="Dossier supprimé avec succès",
        status_code=status.HTTP_200_OK,
    )
