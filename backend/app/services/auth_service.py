from datetime import datetime, timedelta

from fastapi import HTTPException, status
from fastapi import Request
from passlib.context import CryptContext


from app.schemas.auth import UserCreate, UserLogin
# from app.services.minio.bucket_service import BucketService


from core.config import settings
from core.logging import setup_logger
from core.security import JWTService

from database.services.user import create_user, get_email_owner
# from database.services.token import create_token


logger = setup_logger(__name__)


class AuthService:
    """
    Service d'authentification gérant le hachage des mots de passe et la génération de tokens JWT.
    Utilise bcrypt pour le hachage et JWT pour les tokens.
    """

    def __init__(self, connection_manager):
        self.connection_manager = connection_manager
        self.pwd_context = CryptContext(
            schemes=["argon2"],
            deprecated="auto",
            argon2__rounds=12,  # Nombre d'itérations
            argon2__memory_cost=65536,  # Mémoire utilisée (en KiB)
            argon2__parallelism=2,  # Nombre de threads
        )
        self.SECRET_KEY: str = settings.SECRET_KEY
        self.ALGORITHM: str = settings.ALGORITHM
        self.jwt_service: JWTService = JWTService(self.connection_manager)

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

    async def auth_create_user(self, payload: UserCreate):
        """
        Crée un nouvel utilisateur => Le stock en BDD, lui créer un bucket minio ect... .

        Args:
            request : sur le modèle de UserCreate

        Returns:
            User: Utilisateur créé (sans le mot de passe haché).

        Raises:
            HTTPException: Si l'email existe déjà ou en cas d'erreur DB.
        """

        existing_user = get_email_owner(self.connection_manager, payload.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                detail="Un utilisateur avec cet email existe déjà.",
            )

        password_hash = await self.get_password_hash(payload.password)

        payload_data = {
            "username": payload.username,
            "email": payload.email,
            "password": password_hash,
            "full_name": payload.name,
        }

        now = str(datetime.now())

        user = create_user(self.connection_manager, **payload_data, creation_date=now)

        # await BucketService().create_user_bucket()

        # token = self.jwt_service.create_access_token(
        #     {
        #         "sub": payload.email,
        #         "user_id": user.id,
        #         "username": user.username,
        #     }
        # )


        # token = create_token(
        #     self.connection_manager,
        #     token=token,
        #     scope="['*']",
        #     user_id=43,
        #     expiration_date=token.expires_at,
        #     creation_date=token.created_at,
        # )

        return {"user": user}

    async def login_user(self, payload: UserLogin):
        # user = get_user_by_email(self.connection_manager, payload.email)

        # if not user:
        #     raise HTTPException(
        #         status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
        #         detail="Email ou mot de passe incorrect",
        #     )

        # is_valid_password = await self.verify_password(payload.password, user.password)

        # if not is_valid_password:
        #     raise HTTPException(
        #         status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
        #         detail="Email ou mot de passe incorrect"
        #     )

        # token = self.jwt_service.create_access_token(
        #     {
        #         "sub": payload.email,
        #         "user_id": user.id,
        #         "username": user.username,
        #         "role": user.role,
        #     }
        # )

        # expire = str(
        #     (
        #         datetime.now() + timedelta(days=settings.ACCESS_TOKEN_EXPIRE_DAY)
        #     ).timestamp()
        # )

        # token = create_token(
        #     self.connection_manager,
        #     token=token,
        #     scope="['*']",
        #     user_id=user.id,
        #     expiration_date=expire,
        #     creation_date=str(datetime.now()),
        # )

        # return {
        #     user : user,
        #     token : token,
        # }

        pass

    async def logout_user(self):
        pass


def get_auth_service(request: Request) -> AuthService:
    return AuthService(connection_manager=request.app.state.database)
