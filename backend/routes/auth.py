from fastapi import APIRouter, Depends
from backend.app.services.auth_service import get_auth_service, AuthService
from app.schemas.auth import PasswordVerifyRequest


router = APIRouter(prefix="/auth", tags=["Authentification"])


@router.get("/")
async def hello():
    return {"hello": "World"}


@router.get("/hash-password/{password}")
async def hash_password(
    password: str, auth_service: AuthService = Depends(get_auth_service)
) -> str:
    return auth_service.get_password_hash(password)


@router.post("/verify-password")
async def verify(
    request: PasswordVerifyRequest,
    auth_service: AuthService = Depends(get_auth_service),
):
    return auth_service.verify_password(
        plain_password=request.password, hashed_password=request.hashed_password
    )
