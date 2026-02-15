# Import d'une classe pydantic pour gérer les .env
from pydantic_settings import BaseSettings
from pydantic import computed_field, ValidationError
import sys
from termcolor import colored
# Classe qui va nous permettre d'accéder à notre .env


# Classe qui va nous permettre d'accéder à notre .env


class Settings(BaseSettings):
    
    # Database
    DB_NAME: str
    DB_USER: str
    DB_HOST: str
    DB_PASSWORD: str
    DB_PORT: int = 5432

    # Token
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_DAY: int = 30

    # Configuration Minio
    MINIO_ENDPOINT: str
    MINIO_ACCESS_KEY: str
    MINIO_SECRET_KEY: str
    MINIO_SECURE: bool = False

    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: str | None = None

    # Developemment
    DEBUG: bool = False
    CORS_ORIGINS: list[str] = ["*"]
    PORT: int = 8000

    class Config:
        # Le fichier qu'il doit lire
        env_file = ".env"
        env_file_encoding = "utf-8"

    # Méthode pour récupérer l'adresse de la DB
    @computed_field
    @property
    def database_url(self) -> str:
        """Génère l'URL de connexion à la base de données."""
        return f"postgresql+psycopg2://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:5432/{self.DB_NAME}"

    # Methode pour récupérer le DSN de la DB
    @computed_field
    def get_db_dsn(self) -> str:
        """Génère le DSN de la base de données."""
        return f"host={self.DB_HOST} port={self.DB_PORT} dbname={self.DB_NAME} user={self.DB_USER} password={self.DB_PASSWORD}"

try:
    # Instanciation des paramètres
    settings = Settings()  # type: ignore
except ValidationError as e:
    # Si il manque une variable d'.env, on notifie dans la console
    print(
        colored(
            "\n❌ ERREUR : Variables d'environnement manquantes ou invalides !",
            "red",
            attrs=["bold"],
        )
    )
    print(
        colored(
            "Vérifie que ton fichier `.env` contient bien les variables suivantes :",
            "yellow",
        )
    )
    for error in e.errors():
        missing_field = error["loc"][0]
        print(f"  - {colored(missing_field, 'cyan')}")
        sys.exit(1)
