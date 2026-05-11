from fastapi import APIRouter, Depends, Request, status

from app.schemas.user import PasswordUpdate, User, UserUpdate
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
