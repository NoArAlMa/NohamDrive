from fastapi import APIRouter, HTTPException, UploadFile, Depends, status, Query
from app.services.minio_service import MinioService, get_minio_service
from app.schemas.file_tree import SimpleFileTreeResponse
from app.schemas.files import CreateFolder, FileUploadResponse, RenameItem, MoveItem
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
    response_model=BaseResponse,
)
async def list_path(
    path: str = "", minio_service: MinioService = Depends(get_minio_service)
) -> BaseResponse:
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

    return BaseResponse(
        success=True if tree.items else False,
        data=tree,
        status_code=status.HTTP_200_OK,
        message="Tree loaded",
    )


@router.get("/download/{object_name:path}", status_code=status.HTTP_200_OK)
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
    return await minio_service.download_object(user_id, object_name)


@router.post(
    "/folder",
    response_model=BaseResponse[str],
    status_code=status.HTTP_201_CREATED,
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

    folder_path = await minio_service.create_folder(
        user_id=user_id,
        current_path=request.currentPath,
        folder_path=request.folderPath,
    )
    return BaseResponse(
        success=True,
        data=folder_path,
        message="Dossier créé avec succès.",
        status_code=status.HTTP_201_CREATED,
    )


@router.delete(
    "/object",
    response_model=BaseResponse,
    status_code=status.HTTP_200_OK,
)
async def delete_object_endpoint(
    folder_path: str = Query(..., description="Chemin de l'objet à supprimer"),
    minio_service: MinioService = Depends(get_minio_service),
    user_id: int = 1,
):
    await minio_service.delete_object(user_id, folder_path)

    return BaseResponse(
        success=True,
        data=None,
        message="Objet supprimé avec succès",
        status_code=status.HTTP_200_OK,
    )


@router.patch(
    "/rename",
    response_model=BaseResponse,
    status_code=status.HTTP_200_OK,
)
async def rename_endpoint(
    payload: RenameItem,
    minio_service: MinioService = Depends(get_minio_service),
    user_id: int = 1,
):
    await minio_service.rename(
        user_id=user_id,
        path=payload.path,
        new_name=payload.new_name,
    )

    return BaseResponse(
        success=True,
        data=None,
        message="Renommage effectué avec succès",
    )


@router.post(
    "/move",
    response_model=BaseResponse,
    status_code=status.HTTP_200_OK,
)
async def move_endpoint(
    payload: MoveItem,
    minio_service: MinioService = Depends(get_minio_service),
    user_id: int = 1,  # TODO: Remplacer par l'ID réel (via auth)
) -> BaseResponse:
    """
    Déplace un fichier ou un dossier dans le bucket utilisateur.

    **Args:**
        - **payload (MoveItem):** Objet contenant:
            - `source_path (str)`: Chemin source (ex: "dossier1/fichier.txt" ou "dossier1/").
            - `destination_folder (str)`: Chemin de destination (ex: "dossier2/").
            - `is_folder (bool)`: Si True, traite la source comme un dossier.

    **Returns:**
        - **BaseResponse**: Réponse standard avec:
            - `success (bool)`: Statut de la requête.
            - `data (None)`: Toujours None.
            - `message (str)`: Message de confirmation ou d'erreur.
    """
    try:
        await minio_service.move(
            user_id=user_id,
            source_path=payload.source_path,
            destination_folder=payload.destination_folder,
        )
        return BaseResponse(
            success=True,
            data=None,
            message="Déplacement effectué avec succès.",
        )
    except HTTPException as e:
        raise e
