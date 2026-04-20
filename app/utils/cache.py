import redis as redis_lib
from app.core.config import settings

_client: redis_lib.Redis | None = None


def get_redis() -> redis_lib.Redis:
    global _client
    if _client is None:
        _client = redis_lib.from_url(settings.REDIS_URL, decode_responses=True)
    return _client
