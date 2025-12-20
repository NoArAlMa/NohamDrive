from datetime import datetime, timedelta
from typing import Optional
from fastapi import Depends, HTTPException, status
from passlib.context import CryptContext
from jose import jwt, JWTError

from app.schemas.auth import UserCreate
from core.config import settings
from core.logging import setup_logger
from app.services.minio_service import MinioService, get_minio_service
import uuid

# Configuration du logger pour ce module
logger = setup_logger(__name__)


class AuthService:
    """
    Service d'authentification gérant le hachage des mots de passe et la génération de tokens JWT.
    Utilise bcrypt pour le hachage et PyJWT pour les tokens.
    """

    def __init__(self, minio_client: MinioService):
        """Initialise le service avec les paramètres de sécurité depuis la configuration."""
        self.pwd_context = CryptContext(
            schemes=["argon2"],
            deprecated="auto",
            argon2__rounds=12,  # Nombre d'itérations
            argon2__memory_cost=65536,  # Mémoire utilisée (en KiB)
            argon2__parallelism=2,  # Nombre de threads
        )  # Contexte de hachage des mots de passe (argon2)
        self.SECRET_KEY: str = (
            settings.SECRET_KEY
        )  # Clé secrète pour signer les tokens JWT
        self.ALGORITHM: str = settings.ALGORITHM  # Algorithme de signature
        self.minio_service: MinioService = minio_client  # Le service pour gérer MinIO

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """
        Vérifie si un mot de passe en clair correspond à un hachage.

        Args:
            plain_password: Mot de passe en clair à vérifier.
            hashed_password: Hachage du mot de passe stocké en base de données.

        Returns:
            bool: True si le mot de passe est valide, False sinon.
        """
        try:
            return self.pwd_context.verify(plain_password, hashed_password)
        except Exception as e:
            logger.error(f"Erreur lors de la vérification du mot de passe: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erreur lors de la vérification du mot de passe",
            )

    def get_password_hash(self, password: str) -> str:
        """
        Génère un hachage sécurisé d'un mot de passe en clair.

        Args:
            password: Mot de passe en clair à hacher.

        Returns:
            str: Hachage du mot de passe (bcrypt).
        """
        try:
            return self.pwd_context.hash(password)
        except Exception as e:
            logger.error(f"Erreur lors du hachage du mot de passe: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erreur lors du hachage du mot de passe",
            )

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

    def create_user(self, request: UserCreate):
        """
        Crée un nouvel utilisateur => Le stock en BDD, le .

        Args:
            request : sur le modèle de UserCreate

        Returns:
            User: Utilisateur créé (sans le mot de passe haché).

        Raises:
            HTTPException: Si l'email existe déjà ou en cas d'erreur DB.
        """

        # TODO : Vérifier si l'email existe déjà
        # if existing_user:
        #     raise HTTPException(
        #         status_code=status.HTTP_400_BAD_REQUEST,
        #         detail="Un utilisateur avec cet email existe déjà.",
        #     )

        password_hash = self.get_password_hash(request.password)

        # TODO: Créer l'utilisateur dans la BDD

        # TODO : Créer le bucket du user pour MinIO
        # user_id = None Temporaire le temps de récup le vrai userID
        # self.minio_service.create_user_bucket(user_id)

        token = self.create_access_token(
            {
                "sub": request.email,
            }
        )  # + qlq infos du modele User
        # TODO : Ajouter le token en BDD

        return {"user": {}, "token": token}


def get_auth_service(minio=Depends(get_minio_service)) -> AuthService:
    """
    Fournit une instance du service d'authentification.
    Utilisé pour l'injection de dépendances dans FastAPI.


    Args:
        minio : Une instance de MinioService

    Returns:
        AuthService: Instance du service.
    """
    return AuthService(minio)
