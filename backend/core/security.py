from datetime import datetime, timedelta
from typing import Optional
import uuid
from fastapi import Depends, HTTPException, Request, status
from jose import jwt, JWTError
from app.schemas.token import Token
from app.schemas.user import User
from database.services.token import get_token_owner_info
from core.config import settings
from core.logging import setup_logger


logger = setup_logger(__name__)


class JWTService:
    def __init__(self, connection_manager):
        self.SECRET_KEY = settings.SECRET_KEY
        self.ALGORITHM = settings.ALGORITHM
        self.connection_manager = connection_manager

    def create_access_token(
        self,
        data: dict,
        expires_delta: Optional[timedelta] = None,
        scope: Optional[list[str]] = None,
    ) -> Token:
        """
        Génère un token JWT pour les données fournies.
        """
        try:
            to_encode = data.copy()

            now = datetime.now()

            if expires_delta:
                expire = datetime.now() + expires_delta
            else:
                expire = datetime.now() + timedelta(
                    days=settings.ACCESS_TOKEN_EXPIRE_DAY
                )

            to_encode.update(
                {
                    "exp": expire,
                    "iat": now,
                    "jti": str(uuid.uuid4()),
                    "scope": scope if scope else ["*"],
                }
            )

            metadata: Token = Token(
                token=jwt.encode(
                    to_encode, str(self.SECRET_KEY), algorithm=self.ALGORITHM
                ),
                expiration_date=expire,
                creation_date=datetime.now(),
                scope=scope if scope else ["*"],
            )

            return metadata
        except JWTError as e:
            logger.error(f"Erreur lors de la génération du token JWT: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Impossible de générer le token",
            )
        except Exception as e:
            logger.error(f"Erreur inattendue lors de la génération du token: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erreur serveur lors de la génération du token",
            )

    async def get_current_user(self, request: Request):
        token = self.get_token_from_request(request)

        self.verify_token(token)

        # jti = payload.get("jti")

        token_data = get_token_owner_info(self.connection_manager, token)

        if not token_data:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token invalide ou expiré",
            )

        if not token_data:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Utilisateur introuvable",
            )

        return User(
            id=token_data[0],
            username=token_data[1],
            email=token_data[3],
            full_name=token_data[4],
            creation_date=token_data[5],
        )

    def get_token_from_request(self, request: Request) -> str:
        token = request.cookies.get("access_token")

        if not token:
            # fallback header Authorization
            auth_header = request.headers.get("Authorization")
            if auth_header and auth_header.startswith("Bearer "):
                token = auth_header.split(" ")[1]

        if not token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Token manquant"
            )

        return token

    def decode_token(self, token: str) -> dict:
        logger.info(f"Voici ton token : {token}")
        try:
            payload = jwt.decode(
                token, str(self.SECRET_KEY), algorithms=[self.ALGORITHM]
            )
            return payload

        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Token invalide"
            )

    def verify_token(self, token: str) -> dict:
        payload = self.decode_token(token)

        if "exp" not in payload:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token invalide (exp manquant)",
            )

        return payload

    def get_user_id_from_token(self, payload: dict) -> int:
        user_id = payload.get("user_id")

        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token invalide (user_id manquant)",
            )

        return user_id


def get_token_service(request: Request) -> JWTService:
    return JWTService(request.app.state.database)


async def current_user(
    request: Request,
    token_service: JWTService = Depends(get_token_service),
):
    """
    Renvoie l'utilisateur courant à partir du JWT.
    Utilisable dans les routes via Depends(current_user)
    """
    user = await token_service.get_current_user(request)
    return user
