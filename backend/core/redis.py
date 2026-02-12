import socket
import redis.asyncio as redis
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


async def check_redis_availability() -> redis.Redis | None:
    """
    Vérifie que Redis est disponible avec :
    - Timeout strict
    - Gestion des exceptions réseau
    """
    if not redis_client:
        return None

    try:
        pong = await redis_client.execute_command("PING")
        if pong == "PONG":
            return redis_client
        logger.info("Redis est disponible et opérationnel.")
        return redis_client
    except (ConnectionError, TimeoutError, socket.timeout, RedisError) as e:
        logger.warning(f"Redis indisponible : {e}")
        return None


async def get_healthy_redis() -> redis.Redis | None:
    """
    Retourne un client Redis sain ou None.
    Lève une exception seulement en prod si Redis est indisponible.
    """
    client = await check_redis_availability()

    if client:
        return client

    # Si Redis indisponible
    if not settings.DEBUG:
        logger.critical("Redis indisponible en production.")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Service Redis indisponible (timeout max ~0.5s).",
        )

    logger.critical(
        "Redis indisponible : certaines fonctionnalités seront désactivées."
    )
    return None
