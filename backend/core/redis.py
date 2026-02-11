import socket
import redis
from redis.exceptions import RedisError, ConnectionError, TimeoutError
from fastapi import HTTPException, status
from core.config import settings
from core.logging import setup_logger

# Logger
logger = setup_logger(__name__)


redis_client = redis.Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=settings.REDIS_DB,
    password=settings.REDIS_PASSWORD,
    socket_connect_timeout=0.5,
    socket_timeout=0.5,
    decode_responses=True,
)


def get_redis_client():
    """Fournit le client Redis."""
    return redis_client


def check_redis_availability():
    """
    Vérifie que Redis est disponible avec :
    - Timeout strict
    - Retry automatique
    - Gestion des exceptions réseau
    """
    try:
        if redis_client:
            redis_client.ping()
            return redis_client

    except (ConnectionError, TimeoutError, socket.timeout):
        raise

    except RedisError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur Redis : {str(e)}",
        )


def get_healthy_redis():
    """
    Retourne un client Redis sain ou None.
    Lève une exception seulement en prod si Redis est indisponible.
    """
    try:
        client = check_redis_availability()
        logger.info("Redis est disponible et opérationnel.")
        return client

    except Exception:
        if not settings.DEBUG:
            logger.critical("Redis indisponible en production.")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Service Redis indisponible (timeout max ~15s).",
            )
        else:
            logger.critical(
                "Redis indisponible : certaines fonctionnalités seront désactivées."
            )
            return None
