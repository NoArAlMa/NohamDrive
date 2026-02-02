from fastapi import (
    APIRouter,
    HTTPException,
    Request,
    UploadFile,
    Depends,
    status,
    Query,
)
from fastapi.responses import StreamingResponse
from app.services.minio.minio_service import MinioService, get_minio_service
from app.schemas.file_tree import SimpleFileTreeResponse
from app.schemas.files import (
    CompressItems,
    CreateFolder,
    RenameItem,
    MoveItem,
    CopyItem,
)
from app.utils.response import BaseResponse

from app.services.sse_service import sse_manager
from app.schemas.sse import SSEMessage

router = APIRouter(prefix="/storage", tags=["Storage"])


@router.get("/explorer-info")
async def sse_endpoint(
    request: Request, user_id: int = 1
):  # TODO: Récupérer user_id via auth
    return StreamingResponse(
        sse_manager.add_client(user_id),
        media_type="text/event-stream; charset=utf-8",
    )


@router.post(
    "/upload", response_model=BaseResponse, status_code=status.HTTP_201_CREATED
)
async def upload_file_endpoint(
    file: UploadFile,
    minio_service: MinioService = Depends(get_minio_service),
    user_id: int = 1,  # TODO : À remplacer par l'ID réel (via auth)
    path: str = "",
) -> BaseResponse:
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

    message, metadata = await minio_service.download_service.upload_file(
        user_id, file, path
    )

    sse_message = SSEMessage(
        event="upload",
        user_id=user_id,
        data=metadata.model_dump(),
        message=message,
    )
    await sse_manager.notify_user(user_id, sse_message.model_dump())
    await sse_manager.notify_user(user_id, sse_message.model_dump())
    return BaseResponse(
        data=metadata, message=message, status_code=status.HTTP_201_CREATED
    )


@router.get(
    "/tree",
    response_model=BaseResponse,
)
async def list_path(
    path: str = Query(default="/", description="Chemin du dossier"),
    user_id: int = 1,
    page: int = Query(default=1, description="Numéro de page"),
    per_page: int = Query(default=30, description="Nombre d'items par page"),
    minio_service: MinioService = Depends(get_minio_service),
) -> BaseResponse:
    """
    Liste le contenu d'un chemin dans le bucket utilisateur.
    Args:
        path: Chemin relatif (ex: "dossier1/sous-dossier/"). Par défaut, liste la racine.
    Returns:
        TreeResponse: Arborescence du chemin.
    """

    tree: SimpleFileTreeResponse = await minio_service.simple_list_path(
        user_id=user_id, path=path, per_page=per_page, page=page
    )

    return BaseResponse(
        success=True if tree.items else False,
        data=tree,
        status_code=status.HTTP_200_OK,
        message="Tree loaded",
    )


@router.get(
    "/download/{object_name:path}",
    response_class=StreamingResponse,
)
async def download_file_endpoint(
    object_name: str,
    user_id: int = 1,  # TODO: Remplacer par l'ID réel (via auth)
    minio_service: MinioService = Depends(get_minio_service),
) -> StreamingResponse:
    """
    Télécharge un fichier depuis le bucket utilisateur.

    ***Args:***
         **object_name** (str ): Nom du fichier à télécharger
         **user_id** : ID de l'utilisateur (injecté par l'auth)

    """
    return await minio_service.download_service.download_object(user_id, object_name)


@router.post(
    "/folder",
    response_model=BaseResponse[str],
    status_code=status.HTTP_201_CREATED,
)
async def create_folder_endpoint(
    payload: CreateFolder,
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
    # TODO : Return en tuple
    folder_path = await minio_service.object_service.create_folder(
        user_id=user_id,
        current_path=payload.currentPath,
        folder_path=payload.folderPath,
    )

    sse_message = SSEMessage(
        event="folder_created",
        user_id=user_id,
        data=payload.model_dump(),
        message=f"Fichier {payload.folderPath} créer",
    )
    await sse_manager.notify_user(user_id, sse_message.model_dump())

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
    folder_path: str = Query(description="Chemin de l'objet à supprimer"),
    minio_service: MinioService = Depends(get_minio_service),
    user_id: int = 1,
):
    message, data = await minio_service.object_service.delete_object(
        user_id, folder_path
    )

    sse_message = SSEMessage(
        event="delete",
        user_id=user_id,
        data=data,
        message=message,
    )
    await sse_manager.notify_user(user_id, sse_message.model_dump())

    return BaseResponse(
        success=True,
        data=data,
        message=message,
        status_code=status.HTTP_200_OK,
    )


@router.get(
    "/stats",
    response_model=BaseResponse,
    status_code=status.HTTP_200_OK,
)
async def stats_endpoint(
    user_id: int = 1,
    object_path: str = Query(description="Salut toi"),
    minio_service: MinioService = Depends(get_minio_service),
) -> BaseResponse:
    data = await minio_service.object_service.get_object_metadata(user_id, object_path)
    return BaseResponse(
        message="Metadatas du fichier récupérées",
        data=data,
        success=True,
        status_code=200,
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
    message, data = await minio_service.object_service.rename(
        user_id=user_id,
        path=payload.path,
        new_name=payload.new_name,
    )

    sse_message = SSEMessage(
        event="rename",
        user_id=user_id,
        data=data,
        message=message,
    )

    await sse_manager.notify_user(user_id, sse_message.model_dump())
    return BaseResponse(
        success=True, data=data, message=message, status_code=status.HTTP_200_OK
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

    message, data = await minio_service.object_service.move(
        user_id=user_id,
        source_path=payload.source_path,
        destination_folder=payload.destination_folder,
    )

    sse_message = SSEMessage(
        event="move",
        user_id=user_id,
        data=data,
        message=message,
    )
    await sse_manager.notify_user(user_id, sse_message.model_dump())
    await sse_manager.notify_user(user_id, sse_message.model_dump())
    return BaseResponse(
        success=True,
        data=data,
        message=message,
    )


@router.post("/copy", response_model=BaseResponse, status_code=status.HTTP_200_OK)
async def copy_endpoint(
    payload: CopyItem,
    minio_service: MinioService = Depends(get_minio_service),
    user_id: int = 1,  # TODO: Remplacer par l'ID réel (via auth)
):
    message, data = await minio_service.object_service.copy(
        user_id, payload.source_path, payload.destination_folder
    )
    # TODO : Rajouter le nom du dossier (pas assez d'info)

    sse_message = SSEMessage(
        event="copy",
        user_id=user_id,
        data=data,
        message=message,
    )
    await sse_manager.notify_user(user_id, sse_message.model_dump())
    await sse_manager.notify_user(user_id, sse_message.model_dump())
    return BaseResponse(
        success=True, message=message, data=data, status_code=status.HTTP_200_OK
    )


@router.post(
    "/compress", response_model=BaseResponse, status_code=status.HTTP_201_CREATED
)
async def compress_files_endpoint(
    request: CompressItems,
    minio_service: MinioService = Depends(get_minio_service),
    user_id: int = 1,  # TODO : À remplacer par l'ID réel (via auth)
) -> BaseResponse:
    """
    Compresses des fichiers dans le bucket utilisateur.

    Args:
        file : Un fichier à uploader
        user_id : ID de l'utilisateur (injecté par l'auth)

    Returns:
        Le fichier à télécharger
    """

    message, metadata = await minio_service.object_service.compress_objects(
        "user-1", request.objects, request.destination_folder
    )
    return BaseResponse(
        data=metadata, message=message, status_code=status.HTTP_201_CREATED
    )


@router.get("/resolve", response_model=BaseResponse)
async def resolve_path(
    path: str = Query(default="/", description="Chemin du dossier"),
    minio_service: MinioService = Depends(get_minio_service),
    user_id: int = 1,
):
    data = await minio_service.object_service.resolve_objet(user_id=user_id, path=path)
    return BaseResponse(data=data, message="message", status_code=status.HTTP_200_OK)
