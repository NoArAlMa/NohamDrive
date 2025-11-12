# Import d'une classe pydantic pour gérer les .env
from pydantic_settings import BaseSettings

# Classe qui va nous permettre d'accéder à notre .env

class Settings(BaseSettings):
    
    # Database
    
    DB_NAME: str
    DB_USER: str
    DB_HOST: str
    DB_PASSWORD: str
    
    # Token 
    secret_key: str
    algorithm: str = "HS256"
    
    #Developemment
    DEBUG : bool
   
    class Config:
        # Le fichier qu'il doit lire
        env_file = ".env"
        env_file_encoding = "utf-8"
        
        
 
    @property
    def database_url(self):
        """Génère l'URL de connexion à la base de données."""
        return f"postgresql+psycopg2://{self.db_user}:{self.db_password}@{self.db_host}:5432/{self.db_name}"


settings = Settings()