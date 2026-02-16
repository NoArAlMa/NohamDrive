from datetime import datetime, timedelta
from typing import Optional
import uuid
from fastapi import HTTPException, status
from jose import jwt, JWTError
from core.config import settings
from core.logging import setup_logger


logger = setup_logger(__name__)


class JWTService:
    def __init__(self):
        self.SECRET_KEY = settings.SECRET_KEY
        self.ALGORITHM = settings.ALGORITHM

    def create_access_token(
        self,
        data: dict,
        expires_delta: Optional[timedelta] = None,
        scope: Optional[list[str]] = None,
    ) -> dict:
        """
        Génère un token JWT pour les données fournies.

        Args:
            data: Données à encoder dans le token (ex: {"sub": "email@example.com"}).
            expires_delta: Durée de validité du token. Si None, utilise la valeur par défaut.

        Returns:
            str: Token JWT signé.

        Raises:
            HTTPException: En cas d'erreur de génération du token.
        """
        try:
            to_encode = data.copy()

            now = int(datetime.now().timestamp())

            if expires_delta:
                expire = int((datetime.now() + expires_delta).timestamp())
            else:
                expire = int(
                    (
                        datetime.now()
                        + timedelta(days=settings.ACCESS_TOKEN_EXPIRE_DAY)
                    ).timestamp()
                )

            to_encode.update(
                {
                    "exp": expire,
                    "iat": now,
                    "jti": str(uuid.uuid4()),
                    "scope": scope if scope else ["*"],
                }
            )

            metadata = {
                "token": jwt.encode(
                    to_encode, str(self.SECRET_KEY), algorithm=self.ALGORITHM
                ),
                "expires_at": expire,
                "created_at": datetime.now(),
                "scope": scope if scope else ["*"],
            }

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
