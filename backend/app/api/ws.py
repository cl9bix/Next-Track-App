from __future__ import annotations

import json
from typing import Optional

from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_async_session
from app.services.live_bus import bus  # твій LocalBus/RedisBus
from app.crud.events import get_latest_event_by_club_slug  # <- твоя функція (повертає EventResponse)


router = APIRouter()


async def _resolve_event_id_by_club_slug(db: AsyncSession, club_slug: str) -> Optional[int]:
    """
    Беремо latest event по club_slug так само, як REST /events/{club_slug}.
    """
    ev = await get_latest_event_by_club_slug(db, club_slug)
    return getattr(ev, "id", None) or getattr(ev, "event_id", None)


@router.websocket("/ws/events/{club_slug}")
async def ws_event(websocket: WebSocket, club_slug: str, db: AsyncSession = Depends(get_async_session)):
    """
    WS: клієнт підключається по club_slug, бек резолвить event_id і підписується на topic event:{event_id}
    """
    await websocket.accept()

    event_id = await _resolve_event_id_by_club_slug(db, club_slug)
    if not event_id:
        await websocket.send_text(json.dumps({"type": "error", "detail": "Event not found"}, ensure_ascii=False))
        await websocket.close(code=4404)
        return

    topic = f"event:{event_id}"
    q = await bus.subscribe(topic)

    try:
        while True:
            payload = await q.get()
            await websocket.send_text(json.dumps(payload, ensure_ascii=False))
    except WebSocketDisconnect:
        pass
    except Exception:
        try:
            await websocket.close(code=1011)
        except Exception:
            pass
    finally:
        try:
            bus.unsubscribe(topic, q)
        except Exception:
            pass
        try:
            await websocket.close()
        except Exception:
            pass
