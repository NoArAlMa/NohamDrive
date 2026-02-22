from core.logging import setup_logger


logger = setup_logger(__name__)


class UserService:
    def __init__(self):
        pass

    # Créer un utilisateur

    # Récupérer un utilisateur par id

    # Récupérer par email

    # Update profil

    # Delete user


def get_user_service() -> UserService:
    return UserService()
