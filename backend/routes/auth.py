from fastapi import APIRouter, Depends, Request
from app.services.auth_service import get_auth_service, AuthService
from app.schemas.auth import UserCreate, UserLogin
from app.utils.response import BaseResponse
from core.limiter import limiter


router = APIRouter(prefix="/auth", tags=["Authentification"])


@router.post("/register", status_code=201, response_model=BaseResponse)
@limiter.limit("1/minute")
async def create_user_endpoint(
    request: Request,
    payload: UserCreate,
    auth_service: AuthService = Depends(get_auth_service),
):
    # created_user = auth_service.create_user(payload)
    created_user = {"lala": "lala"}
    return BaseResponse(success=True, data=created_user)


@router.post("/login", status_code=200, response_model=BaseResponse)
@limiter.limit("10/minute")
async def login_user_endpoint(
    request: Request,
    payload: UserLogin,
    auth_service: AuthService = Depends(get_auth_service),
):
    return BaseResponse(success=True, data=payload)
