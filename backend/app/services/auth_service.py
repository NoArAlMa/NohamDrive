import logging
from datetime import datetime, timedelta
from typing import Optional
from fastapi import HTTPException, status
from passlib.context import CryptContext
from jose import jwt, JWTError
from core.config import settings

# Configuration du logger pour ce module
logger = logging.getLogger(__name__)


class AuthService:
    """
    Service d'authentification gérant le hachage des mots de passe et la génération de tokens JWT.
    Utilise bcrypt pour le hachage et PyJWT pour les tokens.
    """

    def __init__(self):
        """Initialise le service avec les paramètres de sécurité depuis la configuration."""
        self.pwd_context = CryptContext(
            schemes=["argon2"],
            deprecated="auto",
            argon2__rounds=12,  # Nombre d'itérations
            argon2__memory_cost=65536,  # Mémoire utilisée (en KiB)
            argon2__parallelism=2,  # Nombre de threads
        )  # Contexte de hachage des mots de passe (bcrypt)
        self.SECRET_KEY: str = (
            settings.SECRET_KEY
        )  # Clé secrète pour signer les tokens JWT
        self.ALGORITHM: str = settings.ALGORITHM  # Algorithme de signature

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

        Args:a
            password: Mot de passe en clair à hacher.

        Returns:
            str: Hachage du mot de passe (bcrypt).
        """
        try:
            password = password[:72]
            return self.pwd_context.hash(password)
        except Exception as e:
            logger.error(f"Erreur lors du hachage du mot de passe: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erreur lors du hachage du mot de passe",
            )

    def create_access_token(
        self, data: dict, expires_delta: Optional[timedelta] = None
    ) -> str:
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
            # Utilise UTC pour éviter les problèmes de fuseaux horaires
            expire = datetime.now() + (
                expires_delta or timedelta(days=settings.ACCESS_TOKEN_EXPIRE_DAY)
            )
            to_encode.update({"exp": expire})
            return jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)
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


def get_auth_service() -> AuthService:
    """
    Fournit une instance du service d'authentification.
    Utilisé pour l'injection de dépendances dans FastAPI.

    Returns:
        AuthService: Instance du service.
    """
    return AuthService()
