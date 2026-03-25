from fastapi import APIRouter, Depends, Request, status
from app.services.auth_service import get_auth_service, AuthService
from app.schemas.auth import UserCreate, UserLogin
from app.utils.response import BaseResponse
from app.schemas.user import User
from core.security import current_user
from core.limiter import limiter
from database.services.setup import (
    create_tokens_table,
    create_users_table,
    drop_tokens_table,
    drop_users_table,
)


router = APIRouter(prefix="/auth", tags=["Authentification"])


@router.post("/register", status_code=201, response_model=BaseResponse)
@limiter.limit("3/minute")
async def create_user_endpoint(
    request: Request,
    payload: UserCreate,
    auth_service: AuthService = Depends(get_auth_service),
):
    created_user = await auth_service.auth_create_user(payload)
    return BaseResponse(
        success=True,
        data=created_user,
        status_code=status.HTTP_200_OK,
        message="Sign up successfully",
    )


@router.post("/login", status_code=200, response_model=BaseResponse)
@limiter.limit("5/minute")
async def login_user_endpoint(
    request: Request,
    payload: UserLogin,
    auth_service: AuthService = Depends(get_auth_service),
):
    login_user = await auth_service.auth_login_user(payload)
    return BaseResponse(
        success=True,
        data=login_user,
        status_code=status.HTTP_200_OK,
        message="Login successfully",
    )


@router.post("/logout", status_code=200, response_model=BaseResponse)
@limiter.limit("2/minute")
async def logout_user_endpoint(
    request: Request,
    user: User = Depends(current_user),
    auth_service: AuthService = Depends(get_auth_service),
):
    await auth_service.logout_user(user)
    return BaseResponse(
        success=True, data=None, message="Logout successful", status_code=200
    )


@router.post("/init-db")
async def init_db(request: Request):
    create_users_table(request.app.state.database)
    create_tokens_table(request.app.state.database)

    return {"message": "Database initialized"}


@router.post("/drop-db")
async def drop_db(request: Request):
    drop_tokens_table(request.app.state.database)
    drop_users_table(request.app.state.database)

    return {"message": "Database dropped"}
