from slowapi import Limiter
from slowapi.util import get_remote_address
from core.config import settings
from core.redis import get_healthy_redis

# redis_client = get_healthy_redis()

limiter: Limiter = Limiter(key_func=get_remote_address)


# limiter = Limiter(
#     key_func=get_remote_address,
#     storage_uri=f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}",
# )

# Désactivation propre si Redis down
# if not redis_client:
#     limiter.enabled = False
