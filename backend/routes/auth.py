from fastapi import APIRouter, Depends, Request
from app.services.auth_service import get_auth_service, AuthService
from app.schemas.auth import UserCreate, UserLogin
from app.utils.response import BaseResponse
from core.limiter import limiter
from database.services.setup import (
    create_tokens_table,
    create_users_table,
    drop_tokens_table,
    drop_users_table,
)


router = APIRouter(prefix="/auth", tags=["Authentification"])


@router.post("/register", status_code=201, response_model=BaseResponse)
@limiter.limit("1/minute")
async def create_user_endpoint(
    request: Request,
    payload: UserCreate,
    auth_service: AuthService = Depends(get_auth_service),
):
    created_user = await auth_service.auth_create_user(payload)
    return BaseResponse(success=True, data=created_user)


@router.post("/login", status_code=200, response_model=BaseResponse)
@limiter.limit("10/minute")
async def login_user_endpoint(
    request: Request,
    payload: UserLogin,
    auth_service: AuthService = Depends(get_auth_service),
):
    return BaseResponse(success=True, data=payload)


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
