from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel

from app.api.jwt_guard import require_user
from app.core.redis_client import redis_client
from app.services.event_keys import k_state
from app.services.event_runtime import (
    Track,
    enqueue_track,
    get_queue_snapshot,
    start_event_if_needed,
    end_event,
    vote as vote_track,
)

router = APIRouter(prefix="/api/events", tags=["events"])


class SuggestIn(BaseModel):
    # якщо з autocomplete є готовий id типу "deezer:123" — передай його
    track_id: str | None = None
    title: str
    artist: str | None = None
    cover_url: str | None = None
    duration_sec: int | None = None


class VoteIn(BaseModel):
    track_id: str


@router.post("/{event_id}/start")
async def start_event(event_id: int):
    await start_event_if_needed(event_id)
    return {"ok": True}


@router.post("/{event_id}/end")
async def end_event_route(event_id: int):
    await end_event(event_id)
    return {"ok": True}


@router.get("/{event_id}/state")
async def get_state(event_id: int):
    st = await redis_client.hgetall(k_state(event_id))
    return {"state": st or {}}


@router.get("/{event_id}/queue")
async def get_queue(event_id: int, limit: int = 10):
    items = await get_queue_snapshot(event_id, limit=limit)
    return {"items": items}


@router.post("/{event_id}/suggest")
async def suggest(event_id: int, payload: SuggestIn, tg_id: int = Depends(require_user)):
    # автоматично робимо live
    await start_event_if_needed(event_id)

    # стабільний track_id:
    # - якщо прийшов з пошуку (deezer:/itunes:) — використовуємо його
    # - якщо вручну — робимо user:... щоб не ламати систему
    track_id = payload.track_id or f"user:{tg_id}:{payload.title.strip().lower()}"

    try:
        await enqueue_track(
            event_id,
            Track(
                track_id=track_id,
                title=payload.title.strip(),
                artist=(payload.artist or "").strip() or None,
                cover_url=payload.cover_url,
                duration_sec=payload.duration_sec,
            ),
        )
    except Exception as e:
        raise HTTPException(400, str(e))
    return {"ok": True}


@router.post("/{event_id}/vote")
async def vote(event_id: int, payload: VoteIn, tg_id: int = Depends(require_user)):
    try:
        await vote_track(event_id, tg_id, payload.track_id)
    except ValueError as e:
        raise HTTPException(400, str(e))
    return {"ok": True}
