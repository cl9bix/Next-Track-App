from __future__ import annotations

import os
from typing import Optional

import redis.asyncio as redis


REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")

_redis: Optional[redis.Redis] = None


def get_redis() -> redis.Redis:
    global _redis
    if _redis is None:
        _redis = redis.from_url(
            REDIS_URL,
            encoding="utf-8",
            decode_responses=True,
        )
    return _redis


async def close_redis() -> None:
    global _redis
    if _redis is not None:
        await _redis.aclose()
        _redis = None
