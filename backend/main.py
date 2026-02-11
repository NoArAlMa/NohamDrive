from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from core.redis import get_healthy_redis
from routes import storages, auth
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
from core.config import settings
from core.minio_client import get_healthy_minio
from datetime import datetime
from slowapi.errors import RateLimitExceeded
from core.limiter import limiter


@asynccontextmanager
# Fonction qui s'exécute au démarrage de FastAPI
async def lifespan(app: FastAPI):
    # Injection du client MinIO
    app.state.minio_client = get_healthy_minio()
    app.state.redis = get_healthy_redis()
    if app.state.redis:
        limiter._storage_uri = f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}"
        limiter.enabled = True
    else:
        limiter.enabled = False

    app.state.limiter = limiter
    yield
    app.state.minio_client = None
    app.state.redis = None
    app.state.limiter = None


# Instanciation de l'app FastAPI

app = FastAPI(
    title="NohamDrive API",
    description="API pour NohamDrive un service de stockage cloud type OneDrive.",
    version="0.2.0",
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
    openapi_url="/openapi.json" if settings.DEBUG else None,
    lifespan=lifespan,
)


@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(
        status_code=429,
        content={
            "success": False,
            "data": None,
            "message": "Too many requests",
            "timestamp": datetime.now().isoformat(),
            "status_code": 429,
        },
    )


# Création d'un CORS pour gérer la sécurité (entrées / sorties)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)


@app.middleware("http")
async def restrict_docs(request: Request, call_next):
    if not settings.DEBUG and request.url.path in ["/docs", "/redoc", "/openapi.json"]:
        return JSONResponse(
            content={
                "success": False,
                "data": None,
                "message": "Not Found",
                "timestamp": datetime.now().isoformat(),
                "status_code": 404,
            },
            status_code=404,
        )
    return await call_next(request)


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
            "message": "Erreur interne du serveur",
            "timestamp": datetime.now().isoformat(),
            "status_code": 500,
        },
    )


@app.get("/")
def read_root():
    return {"message": "Bienvenue sur l'API OneDrive Alternative !"}
