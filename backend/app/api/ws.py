from __future__ import annotations

import asyncio
import json
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.services.live_bus import bus  # твій LocalBus/RedisBus

router = APIRouter()

@router.websocket("/ws/events/{event_id}")
async def ws_event(websocket: WebSocket, event_id: int):
    await websocket.accept()
    topic = f"event:{event_id}"
    q = await bus.subscribe(topic)

    try:
        while True:
            payload = await q.get()
            await websocket.send_text(json.dumps(payload, ensure_ascii=False))
    except WebSocketDisconnect:
        pass
    finally:
        bus.unsubscribe(topic, q)
        await websocket.close()
