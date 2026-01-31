from __future__ import annotations

import json
from typing import Optional

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.live_bus import bus

from app.models.session import async_session as async_session_maker

from app.crud.events import get_latest_event_by_club_slug


router = APIRouter()


async def _resolve_event_id_by_club_slug(db: AsyncSession, club_slug: str) -> Optional[int]:
    ev = await get_latest_event_by_club_slug(db, club_slug)

    v = getattr(ev, "id", None) or getattr(ev, "event_id", None)
    if isinstance(v, int) and v > 0:
        return v

    if isinstance(ev, dict):
        v = ev.get("id") or ev.get("event_id")
        if isinstance(v, int) and v > 0:
            return v

    return None


@router.websocket("/ws/events/{club_slug}")
async def ws_event(websocket: WebSocket, club_slug: str):
    """
    Client connects using club_slug, backend resolves latest event_id and subscribes to bus topic event:{event_id}
    """
    await websocket.accept()

    topic: Optional[str] = None
    q = None

    try:
        async with async_session_maker() as db:
            event_id = await _resolve_event_id_by_club_slug(db, club_slug)

            if not event_id:
                await websocket.send_text(json.dumps({"type": "error", "detail": "Event not found"}, ensure_ascii=False))
                await websocket.close(code=4404)
                return

            topic = f"event:{event_id}"
            q = await bus.subscribe(topic)

            while True:
                payload = await q.get()
                await websocket.send_text(json.dumps(payload, ensure_ascii=False))

    except WebSocketDisconnect:
        pass
    except Exception as e:
        try:
            await websocket.send_text(json.dumps({"type": "error", "detail": str(e)}, ensure_ascii=False))
        except Exception:
            pass
        try:
            await websocket.close(code=1011)
        except Exception:
            pass
    finally:
        try:
            if topic and q:
                bus.unsubscribe(topic, q)
        except Exception:
            pass
        try:
            await websocket.close()
        except Exception:
            pass
