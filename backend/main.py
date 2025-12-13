from fastapi import FastAPI
from routes import storages, auth
from fastapi.middleware.cors import CORSMiddleware
from core.config import settings


# Instanciation de l'app FastAPI

app = FastAPI(title="OneDrive Alternative API", version="0.1.0")


# Création d'un CORS pour gérer la sécurité (entrées / sorties)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)


# On inclut les différentes routes du projet

app.include_router(storages.router)
app.include_router(auth.router)


@app.get("/")
def read_root():
    return {"message": "Bienvenue sur l'API OneDrive Alternative !"}
