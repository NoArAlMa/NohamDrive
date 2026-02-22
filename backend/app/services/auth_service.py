from fastapi import HTTPException, status
from passlib.context import CryptContext


from app.schemas.auth import UserCreate
from core.config import settings
from core.logging import setup_logger
from core.security import JWTService


logger = setup_logger(__name__)


class AuthService:
    """
    Service d'authentification gérant le hachage des mots de passe et la génération de tokens JWT.
    Utilise bcrypt pour le hachage et JWT pour les tokens.
    """

    def __init__(self):
        """Initialise le service avec les paramètres de sécurité depuis la configuration."""
        self.pwd_context = CryptContext(
            schemes=["argon2"],
            deprecated="auto",
            argon2__rounds=12,  # Nombre d'itérations
            argon2__memory_cost=65536,  # Mémoire utilisée (en KiB)
            argon2__parallelism=2,  # Nombre de threads
        )
        self.SECRET_KEY: str = settings.SECRET_KEY
        self.ALGORITHM: str = settings.ALGORITHM
        self.jwt_service: JWTService = JWTService()

    async def verify_password(self, plain_password: str, hashed_password: str) -> bool:
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

    async def get_password_hash(self, password: str) -> str:
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

    async def create_user(self, request: UserCreate):
        """
        Crée un nouvel utilisateur => Le stock en BDD, lui créer un bucket minio, lui créer un avatar ect... .

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

        # password_hash = self.get_password_hash(request.password)

        # TODO: Créer l'utilisateur et l'ajouter dans la BDD

        # TODO : Créer le bucket du user pour MinIO

        token = self.jwt_service.create_access_token(
            {
                "sub": request.email,
            }
        )  # + qlq infos du modele User

        # TODO : Ajouter le token en BDD

        return {"user": {}, "token": token}

    async def login_user(self):
        pass

    async def logout_user(self):
        pass


def get_auth_service() -> AuthService:
    """
    Fournit une instance du service d'authentification.
    """
    return AuthService()
