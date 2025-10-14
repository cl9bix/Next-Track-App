from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.services.live_bus import bus

router = APIRouter(tags=["ws"])

@router.websocket("/ws/events/{event_id}")
async def ws_event(websocket: WebSocket, event_id: int):
    await websocket.accept()
    topic = f"event:{event_id}"
    q = await bus.subscribe(topic)
    try:
        while True:
            msg = await q.get()
            await websocket.send_json(msg)
    except WebSocketDisconnect:
        bus.unsubscribe(topic, q)
