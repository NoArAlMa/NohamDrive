from minio import Minio
from minio.error import S3Error
from fastapi import HTTPException, status
from core.config import settings
import logging
import urllib3
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
)
import socket

# Configure le logger

logging.basicConfig(
    level=logging.INFO,  # Affiche INFO et au-dessus (WARNING, ERROR, etc.)
    format="%(levelname)s:     %(message)s",
    handlers=[
        logging.StreamHandler(),  # Affiche les logs dans la console
    ],
)


logger = logging.getLogger(__name__)

# Client MinIO (singleton)
minio_client = Minio(
    endpoint=settings.MINIO_ENDPOINT,
    access_key=settings.MINIO_ACCESS_KEY,
    secret_key=settings.MINIO_SECRET_KEY,
    secure=settings.MINIO_SECURE,
    http_client=urllib3.PoolManager(
        timeout=urllib3.Timeout(connect=2.0, read=3.0),  # Timeout global de 5s
        maxsize=10,
        retries=False,
    ),
)


def get_minio_client():
    """Fournit le client MinIO."""
    return minio_client


@retry(
    stop=stop_after_attempt(3),  # 3 tentatives max
    wait=wait_exponential(multiplier=1, min=1, max=5),  # Délai exponentiel (1s, 2s, 4s)
    retry=retry_if_exception_type(
        (S3Error, socket.timeout, urllib3.exceptions.ReadTimeoutError)
    ),
)
def check_minio_availability():
    """
    Vérifie que MinIO est disponible avec :
    - Timeout strict (5s max par tentative)
    - Retry automatique (3 tentatives)
    - Gestion des exceptions réseau
    """
    try:
        # Utilise un bucket léger pour le check
        minio_client.bucket_exists("minio-health-check")
        return minio_client
    except (S3Error, socket.timeout, urllib3.exceptions.ReadTimeoutError) as e:
        logger.warning(
            f"MinIO indisponible (attempt {retry.statistics['attempt_number']}/3) : {str(e)}"
        )
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur MinIO : {str(e)}",
        )


def get_healthy_minio():
    """
    Retourne un client Minio sain ou None .
    Lève une exception seulement en prod si Minio est indisponible.
    """
    try:
        client = check_minio_availability()
        logger.info("MinIO est disponible et opérationnel.")
        return client

    except Exception:
        if not settings.DEBUG:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Service de stockage indisponible (timeout: 15s max).",
            )
        else:
            logger.critical(
                "MinIO indisponible: certaines fonctionnalités seront désactivées.",
            )
            return None
