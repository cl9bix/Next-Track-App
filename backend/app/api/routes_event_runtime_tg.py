from __future__ import annotations

from typing import Optional
from sqlalchemy import select, func
from sqlalchemy import desc
from fastapi import APIRouter, Depends, Header, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.models import ClubSettings,Club
from app.crud.event_crud import get_latest_event_by_club_slug
from app.models.session import get_async_session
from app.services.event_runtime import (
    Track,
    enqueue_track,
    get_attendees_count,
    get_queue_snapshot,
    register_attendee,
)

router = APIRouter(prefix="/api/v1/events", tags=["event-runtime"])


class QueueAddIn(BaseModel):
    track_id: str = Field(..., min_length=1)
    title: str = Field(..., min_length=1)
    artist: Optional[str] = None
    cover_url: Optional[str] = None
    duration_sec: Optional[int] = None
    telegram_id: Optional[int] = None


async def resolve_event_id(club_slug: str, db: AsyncSession) -> int:
    event = await get_latest_event_by_club_slug(db, club_slug)
    if not event:
        raise HTTPException(status_code=404, detail="Active event not found")
    return event.id


@router.get("/{club_slug}")
async def get_event_summary(
        club_slug: str,
        tg_id: Optional[int] = Header(default=None, alias="X-Telegram-User-Id"),
        db: AsyncSession = Depends(get_async_session),
):
    event = await get_latest_event_by_club_slug(db, club_slug)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    club = (
        await db.execute(
            select(Club).where(Club.id == event.club_id)
        )
    ).scalar_one_or_none()

    settings = None
    if club:
        settings = (
            await db.execute(
                select(ClubSettings).where(ClubSettings.club_id == club.id)
            )
        ).scalar_one_or_none()

    if tg_id:
        attendees_count = await register_attendee(event.id, tg_id)
    else:
        attendees_count = await get_attendees_count(event.id)

    return {
        "id": event.id,
        "club_id": event.club_id,
        "title": event.title,
        "preview": event.preview,
        "start_date": event.start_date,
        "end_date": event.end_date,
        "created_at": getattr(event, "created_at", None),
        "slug": club_slug,
        "attendees_count": attendees_count,
        "background_image_url": (
                getattr(event, "background_image_url", None)
                or (settings.background_image_url if settings else None)
        ),
        "club": {
            "id": club.id,
            "name": club.name,
            "slug": club.slug,
        } if club else None,
    }


@router.get("/{club_slug}/queue")
async def get_queue(
        club_slug: str,
        limit: int = Query(default=20, ge=1, le=200),
        tg_id: Optional[int] = Header(default=None, alias="X-Telegram-User-Id"),
        db: AsyncSession = Depends(get_async_session),
):
    event_id = await resolve_event_id(club_slug, db)

    if tg_id:
        await register_attendee(event_id, tg_id)

    items = await get_queue_snapshot(event_id, limit=limit)
    attendees_count = await get_attendees_count(event_id)

    return {
        "items": items,
        "attendees_count": attendees_count,
    }


@router.post("/{club_slug}/queue")
async def add_to_queue(
        club_slug: str,
        payload: QueueAddIn,
        tg_id: Optional[int] = Header(default=None, alias="X-Telegram-User-Id"),
        db: AsyncSession = Depends(get_async_session),
):
    event_id = await resolve_event_id(club_slug, db)

    effective_tg_id = tg_id or payload.telegram_id

    if effective_tg_id:
        await register_attendee(event_id, effective_tg_id)

    track = Track(
        track_id=payload.track_id,
        title=payload.title,
        artist=payload.artist,
        cover_url=payload.cover_url,
        duration_sec=payload.duration_sec,
        suggested_by=effective_tg_id,
    )

    await enqueue_track(event_id, track)

    return {
        "status": "success",
        "event_id": event_id,
        "track_id": payload.track_id,
    }