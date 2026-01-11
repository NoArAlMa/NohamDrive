from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from routes import storages, auth
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
from core.config import settings
from core.minio_client import get_healthy_minio
from datetime import datetime


@asynccontextmanager
# Fonction qui s'exécute au démarrage de FastAPI
async def lifespan(app: FastAPI):
    # Injection du client MinIO
    app.state.minio_client = get_healthy_minio()
    yield
    app.state.minio_client = None


# Instanciation de l'app FastAPI

app = FastAPI(title="OneDrive Alternative API", version="0.1.0", lifespan=lifespan)


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


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "data": None,
            "message": exc.detail if hasattr(exc, "detail") else "Erreur HTTP",
            "timestamp": datetime.now().isoformat(),
            "status_code": exc.status_code,
        },
    )


# Gestion des erreurs de validation (ex: Query, Body)
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={
            "success": False,
            "data": None,
            "message": str(exc),
            "timestamp": datetime.now().isoformat(),
            "status_code": 422,
        },
    )


# Gestion des exceptions génériques
@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "data": None,
            "message": str(exc),
            "timestamp": datetime.now().isoformat(),
            "status_code": 500,
        },
    )


@app.get("/")
def read_root():
    return {"message": "Bienvenue sur l'API OneDrive Alternative !"}
