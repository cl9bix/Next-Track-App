import asyncio
from typing import Dict, Set, Optional
from app.core.config import settings

# ---------- Local fallback ----------
class LocalBus:
    def __init__(self):
        self._topics: Dict[str, Set[asyncio.Queue]] = {}

    async def publish(self, topic: str, payload: dict):
        for q in list(self._topics.get(topic, set())):
            await q.put(payload)

    async def subscribe(self, topic: str) -> asyncio.Queue:
        q = asyncio.Queue()
        self._topics.setdefault(topic, set()).add(q)
        return q

    def unsubscribe(self, topic: str, q: asyncio.Queue):
        self._topics.get(topic, set()).discard(q)

# ---------- Redis implementation ----------
class RedisBus:
    def __init__(self, url: str):
        import redis.asyncio as redis
        self.redis = redis.from_url(url, decode_responses=True)
        self._tasks: Set[asyncio.Task] = set()

    async def publish(self, topic: str, payload: dict):
        import json
        await self.redis.publish(topic, json.dumps(payload, separators=(",", ":")))

    async def subscribe(self, topic: str) -> asyncio.Queue:
        """
        Повертає локальну asyncio.Queue, а під капотом читає Redis pubsub і кладе в цю чергу.
        """
        import json
        q: asyncio.Queue = asyncio.Queue()
        pubsub = self.redis.pubsub()
        await pubsub.subscribe(topic)

        async def reader():
            try:
                async for msg in pubsub.listen():
                    if msg and msg.get("type") == "message":
                        try:
                            data = json.loads(msg["data"])
                        except Exception:
                            data = {"raw": msg["data"]}
                        await q.put(data)
            finally:
                await pubsub.unsubscribe(topic)
                await pubsub.close()

        task = asyncio.create_task(reader())
        self._tasks.add(task)
        task.add_done_callback(self._tasks.discard)
        # повертаємо тільки Queue; відписка нижче
        q._pubsub = pubsub  # type: ignore[attr-defined]
        return q

    def unsubscribe(self, topic: str, q: asyncio.Queue):
        # pubsub закривається у reader(); тут просто чистимо локальні посилання
        if hasattr(q, "_pubsub"):
            # залишаємо на reader cleanup
            pass

if settings.REDIS_URL:
    bus = RedisBus(settings.REDIS_URL)
else:
    bus = LocalBus()

async def publish_event(event_id: int, payload: dict):
    await bus.publish(f"event:{event_id}", payload)
