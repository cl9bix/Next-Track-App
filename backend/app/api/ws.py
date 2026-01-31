from __future__ import annotations

import json
from typing import Optional, Callable, Awaitable

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.live_bus import bus


router = APIRouter()


# =========================
# Import adapters (NO GUESSING app.db)
# =========================

# --- get_async_session ---
get_async_session: Optional[Callable[[], AsyncSession]] = None

_get_async_session_import_errors = []

try:
    # 1) if you have something like: from app.dependencies import get_async_session
    from app.dependencies import get_async_session as _get_async_session  # type: ignore
    get_async_session = _get_async_session
except Exception as e:
    _get_async_session_import_errors.append(("app.dependencies.get_async_session", repr(e)))

if get_async_session is None:
    try:
        # 2) common pattern: app.core.dependencies
        from app.core.dependencies import get_async_session as _get_async_session  # type: ignore
        get_async_session = _get_async_session
    except Exception as e:
        _get_async_session_import_errors.append(("app.core.dependencies.get_async_session", repr(e)))

if get_async_session is None:
    try:
        # 3) sometimes: app.api.deps
        from app.api.deps import get_async_session as _get_async_session  # type: ignore
        get_async_session = _get_async_session
    except Exception as e:
        _get_async_session_import_errors.append(("app.api.deps.get_async_session", repr(e)))

if get_async_session is None:
    try:
        # 4) sometimes: app.api.dependencies
        from app.api.dependencies import get_async_session as _get_async_session  # type: ignore
        get_async_session = _get_async_session
    except Exception as e:
        _get_async_session_import_errors.append(("app.api.dependencies.get_async_session", repr(e)))

if get_async_session is None:
    # If you already know the real path, replace the block above with your correct import.
    raise ModuleNotFoundError(
        "Cannot import get_async_session. Tried:\n"
        + "\n".join([f"- {p}: {err}" for p, err in _get_async_session_import_errors])
    )


# --- get_latest_event_by_club_slug ---
get_latest_event_by_club_slug: Optional[Callable[[AsyncSession, str], Awaitable[object]]] = None

_get_latest_event_import_errors = []

try:
    # 1) if your CRUD is in app.crud.events
    from app.crud.events import get_latest_event_by_club_slug as _get_latest_event_by_club_slug  # type: ignore
    get_latest_event_by_club_slug = _get_latest_event_by_club_slug
except Exception as e:
    _get_latest_event_import_errors.append(("app.crud.events.get_latest_event_by_club_slug", repr(e)))

if get_latest_event_by_club_slug is None:
    try:
        # 2) sometimes in app.services.events
        from app.services.events import get_latest_event_by_club_slug as _get_latest_event_by_club_slug  # type: ignore
        get_latest_event_by_club_slug = _get_latest_event_by_club_slug
    except Exception as e:
        _get_latest_event_import_errors.append(("app.services.events.get_latest_event_by_club_slug", repr(e)))

if get_latest_event_by_club_slug is None:
    try:
        # 3) sometimes in app.api.v1.events (router module)
        from app.api.v1.events import get_latest_event_by_club_slug as _get_latest_event_by_club_slug  # type: ignore
        get_latest_event_by_club_slug = _get_latest_event_by_club_slug
    except Exception as e:
        _get_latest_event_import_errors.append(("app.api.v1.events.get_latest_event_by_club_slug", repr(e)))

if get_latest_event_by_club_slug is None:
    raise ModuleNotFoundError(
        "Cannot import get_latest_event_by_club_slug. Tried:\n"
        + "\n".join([f"- {p}: {err}" for p, err in _get_latest_event_import_errors])
    )


# =========================
# Logic
# =========================

async def _resolve_event_id_by_club_slug(db: AsyncSession, club_slug: str) -> Optional[int]:
    ev = await get_latest_event_by_club_slug(db, club_slug)  # type: ignore[misc]
    # ev is likely pydantic (EventResponse) or ORM model. Support both.
    for attr in ("id", "event_id"):
        v = getattr(ev, attr, None)
        if isinstance(v, int) and v > 0:
            return v
    # sometimes dict-like
    if isinstance(ev, dict):
        v = ev.get("id") or ev.get("event_id")
        if isinstance(v, int) and v > 0:
            return v
    return None


@router.websocket("/ws/events/{club_slug}")
async def ws_event(websocket: WebSocket, club_slug: str):
    """
    WS connects by club_slug; backend resolves latest event_id and subscribes to bus topic event:{event_id}
    """
    await websocket.accept()

    # open db session manually (no Depends for websocket)
    db: Optional[AsyncSession] = None
    topic: Optional[str] = None
    q = None

    try:
        db = get_async_session()  # type: ignore[call-arg]
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
            if db is not None:
                await db.close()
        except Exception:
            pass

        try:
            await websocket.close()
        except Exception:
            pass
