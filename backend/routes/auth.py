from fastapi import APIRouter, Depends
from app.services.auth_service import get_auth_service, AuthService
from app.schemas.auth import UserCreate
from app.utils.response import BaseResponse


router = APIRouter(prefix="/auth", tags=["Authentification"])


@router.post("/register")
async def create_user_endpoint(
    request: UserCreate,
    auth_service: AuthService = Depends(get_auth_service),
):
    created_user = auth_service.create_user(request)
    return BaseResponse(success=True, data=created_user)
