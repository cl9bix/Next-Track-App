from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse,JSONResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.jwt_guard import require_user
from app.core.redis_client import redis_client
from app.models.session import get_async_session
from app.crud.event_crud import (
    list_events,
    get_latest_event_by_club_slug,
)
from app.schemas.schemas import EventResponse,PublicEventResponse
from app.services.event_keys import k_state
from app.services.event_runtime import (
    Track,
    enqueue_track,
    get_queue_snapshot,
    start_event_if_needed,
    end_event,
    vote as vote_track,
)

router = APIRouter(prefix="/api/v1/events", tags=["events"])
templates = Jinja2Templates(directory="templates")

# ==========================
# Schemas
# ==========================

class SuggestIn(BaseModel):
    track_id: str | None = None
    title: str
    artist: str | None = None
    cover_url: str | None = None
    duration_sec: int | None = None


class VoteIn(BaseModel):
    track_id: str


# ==========================
# Helpers
# ==========================

async def resolve_event_id(
    club_slug: str,
    db: AsyncSession,
) -> int:
    """
    Беремо ОСТАННІЙ активний event для клубу.
    Якщо нема — 404.
    """
    event = await get_latest_event_by_club_slug(db, club_slug)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    return event.id


# ==========================
# Public (user)
# ==========================

@router.get("/", response_model=list[EventResponse])
async def list_events_ep(
    db: AsyncSession = Depends(get_async_session),
):
    return await list_events(db)


@router.get("/{club_slug}", response_class=HTMLResponse)
async def get_event_for_users(
    request: Request,
    club_slug: str,
    db: AsyncSession = Depends(get_async_session),
):
    event = await get_latest_event_by_club_slug(db, club_slug)
    if not event:
        print("EVENT NOT FOUND")
        raise HTTPException(status_code=404, detail="Event not found")

    print("ALLES IM ORDNUNG")
    # return templates.TemplateResponse(
    #     "user.html",
    return {'event': event or {}}

@router.get("/{club_slug}/state")
async def get_state(
    club_slug: str,
    db: AsyncSession = Depends(get_async_session),
):
    event_id = await resolve_event_id(club_slug, db)
    st = await redis_client.hgetall(k_state(event_id))
    return {"state": st or {}}


@router.get("/{club_slug}/queue")
async def get_queue(
    club_slug: str,
    limit: int = 10,
    db: AsyncSession = Depends(get_async_session),
):
    event_id = await resolve_event_id(club_slug, db)
    items = await get_queue_snapshot(event_id, limit=limit)
    return {"items": items}


# ==========================
# User actions
# ==========================

@router.post("/{club_slug}/suggest")
async def suggest(
    club_slug: str,
    payload: SuggestIn,
    tg_id: int = Depends(require_user),
    db: AsyncSession = Depends(get_async_session),
):
    event_id = await resolve_event_id(club_slug, db)

    # автоматично стартуємо івент
    await start_event_if_needed(event_id)

    # стабільний track_id
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
        raise HTTPException(status_code=400, detail=str(e))

    return {"ok": True}


@router.post("/{club_slug}/vote")
async def vote(
    club_slug: str,
    payload: VoteIn,
    tg_id: int = Depends(require_user),
    db: AsyncSession = Depends(get_async_session),
):
    event_id = await resolve_event_id(club_slug, db)

    try:
        await vote_track(event_id, tg_id, payload.track_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return {"ok": True}


# ==========================
# Owner / admin
# ==========================

@router.post("/{club_slug}/start")
async def start_event_route(
    club_slug: str,
    db: AsyncSession = Depends(get_async_session),
):
    event_id = await resolve_event_id(club_slug, db)
    await start_event_if_needed(event_id)
    return {"ok": True}


@router.post("/{club_slug}/end")
async def end_event_route(
    club_slug: str,
    db: AsyncSession = Depends(get_async_session),
):
    event_id = await resolve_event_id(club_slug, db)
    await end_event(event_id)
    return {"ok": True}
