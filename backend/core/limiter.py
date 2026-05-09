from slowapi import Limiter
from slowapi.util import get_remote_address
from core.config import settings


limiter: Limiter = Limiter(
    key_func=get_remote_address,
    storage_uri=f"redis://:{settings.REDIS_PASSWORD}@{settings.REDIS_HOST}:{settings.REDIS_PORT}",
)
