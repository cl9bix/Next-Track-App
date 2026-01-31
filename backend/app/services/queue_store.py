from __future__ import annotations

import json
import time
from dataclasses import asdict, dataclass
from typing import Any, Dict, List, Optional

from app.core.redis import get_redis


@dataclass
class QueueItem:
    track_id: str
    title: str
    artist: Optional[str] = None
    cover_url: Optional[str] = None
    duration_sec: Optional[int] = None

    # optional metadata:
    suggested_by_tg_id: Optional[int] = None
    created_at: int = 0

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> "QueueItem":
        return QueueItem(
            track_id=str(d.get("track_id") or ""),
            title=str(d.get("title") or ""),
            artist=d.get("artist") or None,
            cover_url=d.get("cover_url") or None,
            duration_sec=d.get("duration_sec") if d.get("duration_sec") is not None else None,
            suggested_by_tg_id=d.get("suggested_by_tg_id") if d.get("suggested_by_tg_id") is not None else None,
            created_at=int(d.get("created_at") or 0),
        )


class RedisQueueStore:
    """
    Queue is stored as:
      - list:  event:{event_id}:queue         -> JSON items (append)
      - index: event:{event_id}:queue:index   -> hash track_id -> JSON (last version)
    That lets us:
      - return in insertion order from list
      - also update/dedupe via hash if you want later
    """

    def __init__(self) -> None:
        self.r = get_redis()

    @staticmethod
    def _k_queue(event_id: int) -> str:
        return f"event:{event_id}:queue"

    @staticmethod
    def _k_index(event_id: int) -> str:
        return f"event:{event_id}:queue:index"

    async def add(self, event_id: int, item: QueueItem) -> None:
        if not item.created_at:
            item.created_at = int(time.time())

        payload = json.dumps(asdict(item), ensure_ascii=False, separators=(",", ":"))
        qk = self._k_queue(event_id)
        ik = self._k_index(event_id)

        # store
        await self.r.rpush(qk, payload)
        await self.r.hset(ik, item.track_id, payload)

        # optional: keep queue bounded (e.g. last 200 items)
        await self.r.ltrim(qk, -200, -1)

    async def list(self, event_id: int) -> List[QueueItem]:
        qk = self._k_queue(event_id)
        raw = await self.r.lrange(qk, 0, -1)
        out: List[QueueItem] = []
        for s in raw:
            try:
                out.append(QueueItem.from_dict(json.loads(s)))
            except Exception:
                continue
        return out
