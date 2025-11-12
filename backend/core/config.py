# Import d'une classe pydantic pour gérer les .env
from pydantic_settings import BaseSettings

# Classe qui va nous permettre d'accéder à notre .env
class Settings(BaseSettings):
    
    # Database
    
    db_name: str
    db_user: str
    db_host: str
    db_port: str
    
    # Token 
    secret_key: str
    algorithm: str
   
    class Config:
        # Le fichier qu'il doit lire
        env_file = ".env"


settings = Settings()