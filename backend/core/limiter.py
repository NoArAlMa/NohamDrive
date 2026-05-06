from slowapi import Limiter
from starlette.requests import Request
import hashlib


def get_rate_limit_key(request: Request) -> str:
    # IP réelle
    ip = request.client.host if request.client else "unknown"

    # Headers utiles
    user_agent = request.headers.get("user-agent", "unknown")
    accept_lang = request.headers.get("accept-language", "unknown")

    # Optionnel : cookie/session
    session = request.cookies.get("session", "no-session")

    raw = f"{ip}:{user_agent}:{accept_lang}:{session}"

    return hashlib.sha256(raw.encode()).hexdigest()


limiter: Limiter = Limiter(key_func=get_rate_limit_key)
