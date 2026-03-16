from __future__ import annotations

import json
import time
from dataclasses import asdict, dataclass
from typing import Any, Dict, List, Optional

from app.core.redis_client import redis_client
from app.services.event_keys import (
    k_attendees,
    k_queue_items,
    k_queue_order,
    k_votes,
    k_user_votes,
    k_state,
)


@dataclass
class Track:
    track_id: str
    title: str
    artist: Optional[str] = None
    cover_url: Optional[str] = None
    duration_sec: Optional[int] = None
    suggested_by: Optional[int] = None
    created_at: int = 0

    def to_json(self) -> str:
        d = asdict(self)
        d["track_id"] = str(d.get("track_id") or "").strip()
        d["title"] = str(d.get("title") or "").strip()
        d["artist"] = d.get("artist") or None
        d["cover_url"] = d.get("cover_url") or None
        d["duration_sec"] = d.get("duration_sec")
        d["suggested_by"] = d.get("suggested_by")
        d["created_at"] = int(d.get("created_at") or 0)
        return json.dumps(d, ensure_ascii=False, separators=(",", ":"))

    @staticmethod
    def from_json(s: str) -> "Track":
        obj = json.loads(s)
        return Track(
            track_id=str(obj.get("track_id") or ""),
            title=str(obj.get("title") or ""),
            artist=obj.get("artist") or None,
            cover_url=obj.get("cover_url") or None,
            duration_sec=obj.get("duration_sec") if obj.get("duration_sec") is not None else None,
            suggested_by=obj.get("suggested_by") if obj.get("suggested_by") is not None else None,
            created_at=int(obj.get("created_at") or 0),
        )


async def register_attendee(event_id: int, tg_id: int) -> int:
    if not tg_id:
        return await get_attendees_count(event_id)

    key = k_attendees(event_id)
    await redis_client.sadd(key, str(tg_id))
    return await redis_client.scard(key)


async def get_attendees_count(event_id: int) -> int:
    return int(await redis_client.scard(k_attendees(event_id)) or 0)


async def start_event_if_needed(event_id: int) -> None:
    st_key = k_state(event_id)
    st = await redis_client.hgetall(st_key)
    if not st:
        await redis_client.hset(st_key, mapping={"voting_open": "1"})


async def end_event(event_id: int) -> None:
    await redis_client.hset(k_state(event_id), mapping={"voting_open": "0"})


async def enqueue_track(event_id: int, track: Track) -> None:
    if not track.track_id or not track.title:
        raise ValueError("track_id and title are required")

    if not track.created_at:
        track.created_at = int(time.time())

    payload = track.to_json()

    items_key = k_queue_items(event_id)
    order_key = k_queue_order(event_id)
    votes_key = k_votes(event_id)

    exists = await redis_client.hexists(items_key, track.track_id)
    await redis_client.hset(items_key, track.track_id, payload)

    if not exists:
        await redis_client.rpush(order_key, track.track_id)

    if not await redis_client.hexists(votes_key, track.track_id):
        await redis_client.hset(votes_key, track.track_id, 0)

    await _trim_queue(event_id, max_len=200)


async def _trim_queue(event_id: int, max_len: int = 200) -> None:
    order_key = k_queue_order(event_id)
    items_key = k_queue_items(event_id)
    votes_key = k_votes(event_id)

    length = await redis_client.llen(order_key)
    if length <= max_len:
        return

    to_remove = length - max_len
    removed_ids: List[str] = []
    for _ in range(to_remove):
        tid = await redis_client.lpop(order_key)
        if tid:
            removed_ids.append(tid)

    if removed_ids:
        await redis_client.hdel(items_key, *removed_ids)
        await redis_client.hdel(votes_key, *removed_ids)


async def get_queue_snapshot(event_id: int, limit: int = 10) -> List[Dict[str, Any]]:
    limit = max(1, min(int(limit or 10), 200))

    order_key = k_queue_order(event_id)
    items_key = k_queue_items(event_id)
    votes_key = k_votes(event_id)

    ids = await redis_client.lrange(order_key, 0, limit - 1)
    if not ids:
        return []

    raw_items = await redis_client.hmget(items_key, ids)
    raw_votes = await redis_client.hmget(votes_key, ids)

    out: List[Dict[str, Any]] = []
    for tid, js, v in zip(ids, raw_items, raw_votes):
        if not js:
            continue

        try:
            t = Track.from_json(js)
        except Exception:
            continue

        try:
            votes = int(v or 0)
        except Exception:
            votes = 0

        out.append({
            "track_id": t.track_id or tid,
            "title": t.title,
            "artist": t.artist,
            "cover_url": t.cover_url,
            "duration_sec": t.duration_sec,
            "votes": votes,
            "suggested_by": t.suggested_by,
            "created_at": t.created_at,
        })

    return out