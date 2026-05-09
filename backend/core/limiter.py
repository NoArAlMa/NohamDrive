from slowapi import Limiter
from starlette.requests import Request
import hashlib
from slowapi.util import get_remote_address


limiter: Limiter = Limiter(
    key_func=get_remote_address, storage_uri="redis://localhost:6379"
)
