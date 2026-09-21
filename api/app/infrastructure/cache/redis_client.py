"""Redis connection helpers."""

from __future__ import annotations

from redis.asyncio import Redis

from app.core.config import Settings, get_settings

_client: Redis | None = None


def get_redis(settings: Settings | None = None) -> Redis:
    """Return the process-wide Redis client."""
    global _client
    if _client is None:
        config = settings or get_settings()
        _client = Redis.from_url(str(config.redis_url), encoding="utf-8", decode_responses=True)
    return _client


async def close_redis() -> None:
    """Close the Redis client on application shutdown."""
    global _client
    if _client is not None:
        await _client.aclose()
    _client = None
