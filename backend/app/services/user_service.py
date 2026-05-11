from fastapi import HTTPException, Request, status
from passlib.context import CryptContext

from app.schemas.user import CompleteUser, PasswordUpdate, User, UserUpdate
from core.logging import setup_logger
from database.connection_management import ConnectionManager
from database.services.user import get_user_through_email, update_user


logger = setup_logger(__name__)


class UserService:
    def __init__(self, connection_manager: ConnectionManager):
        self.connection_manager = connection_manager
        self.pwd_context = CryptContext(
            schemes=["argon2"],
            deprecated="auto",
            argon2__rounds=12,
            argon2__memory_cost=65536,
            argon2__parallelism=2,
        )

    # Créer un utilisateur

    # Récupérer un utilisateur par id

    # Récupérer par email

    # Update profil
    async def update_profile(self, current_user: User, payload: UserUpdate) -> User:
        updates = {
            "username": payload.username.strip(),
            "email": str(payload.email).strip(),
            "full_name": payload.full_name.strip(),
        }

        for column, value in updates.items():
            if getattr(current_user, column) != value:
                update_user(self.connection_manager, current_user.id, column, value)

        return User(
            id=current_user.id,
            username=updates["username"],
            email=updates["email"],
            full_name=updates["full_name"],
            creation_date=current_user.creation_date,
        )

    async def update_password(self, current_user: User, payload: PasswordUpdate) -> None:
        user: CompleteUser | None = get_user_through_email(
            self.connection_manager, current_user.email
        )

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Utilisateur introuvable",
            )

        if not self.pwd_context.verify(payload.current_password, user.password):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Mot de passe actuel incorrect",
            )

        password_hash = self.pwd_context.hash(payload.new_password)
        update_user(self.connection_manager, current_user.id, "password", password_hash)

    # Delete user


def get_user_service(request: Request) -> UserService:
    return UserService(request.app.state.database)
