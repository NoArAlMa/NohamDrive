from slowapi import Limiter
from slowapi.util import get_rate_limit_key


limiter: Limiter = Limiter(key_func=get_rate_limit_key)
