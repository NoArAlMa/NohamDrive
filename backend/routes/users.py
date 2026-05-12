from fastapi import APIRouter, Depends, Request, UploadFile, status
from fastapi.responses import Response

from app.schemas.user import PasswordUpdate, User, UserUpdate
from app.services.profile_picture_service import (
    ProfilePictureService,
    get_profile_picture_service,
)
from app.services.user_service import UserService, get_user_service
from app.utils.response import BaseResponse
from core.limiter import limiter
from core.security import current_user

router = APIRouter(prefix="/users", tags=["Users"])


@router.patch("/me", response_model=BaseResponse[User], status_code=status.HTTP_200_OK)
@limiter.limit("10/minute")
async def update_current_user_endpoint(
    request: Request,
    payload: UserUpdate,
    user: User = Depends(current_user),
    user_service: UserService = Depends(get_user_service),
) -> BaseResponse[User]:
    updated_user = await user_service.update_profile(user, payload)
    return BaseResponse(
        success=True,
        data=updated_user,
        message="Profil mis à jour",
        status_code=status.HTTP_200_OK,
    )


@router.patch(
    "/me/password", response_model=BaseResponse[None], status_code=status.HTTP_200_OK
)
@limiter.limit("5/minute")
async def update_current_user_password_endpoint(
    request: Request,
    payload: PasswordUpdate,
    user: User = Depends(current_user),
    user_service: UserService = Depends(get_user_service),
) -> BaseResponse[None]:
    await user_service.update_password(user, payload)
    return BaseResponse(
        success=True,
        data=None,
        message="Mot de passe mis à jour",
        status_code=status.HTTP_200_OK,
    )


@router.get("/me/profile-picture")
@limiter.limit("60/minute")
async def get_my_profile_picture_endpoint(
    request: Request,
    user: User = Depends(current_user),
    pp_service: ProfilePictureService = Depends(get_profile_picture_service),
):
    data, content_type = await pp_service.get_picture(
        user_id=user.id, full_name=user.full_name
    )
    return Response(content=data, media_type=content_type)


@router.post(
    "/me/profile-picture",
    response_model=BaseResponse[dict],
    status_code=status.HTTP_201_CREATED,
)
@limiter.limit("10/minute")
async def upload_my_profile_picture_endpoint(
    request: Request,
    file: UploadFile,
    user: User = Depends(current_user),
    pp_service: ProfilePictureService = Depends(get_profile_picture_service),
) -> BaseResponse[dict]:
    data = await pp_service.set_picture(user_id=user.id, file=file)
    return BaseResponse(
        success=True,
        data=data,
        message="Avatar mis à jour",
        status_code=status.HTTP_201_CREATED,
    )
