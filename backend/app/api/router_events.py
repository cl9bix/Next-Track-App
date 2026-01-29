from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.session import get_async_session
from app.crud.event_crud import list_events,get_latest_event_by_club_slug
from app.schemas.schemas import EventResponse

router = APIRouter(prefix="/api/v1/events", tags=["events"])

@router.get("/", response_model=list[EventResponse])
async def list_events_ep(db: AsyncSession = Depends(get_async_session)):
    return await list_events(db)

@router.get("/{club_slug}", response_model=EventResponse)
async def get_event_for_users(club_slug: str, db: AsyncSession = Depends(get_async_session)):
    return await get_latest_event_by_club_slug(db, club_slug)
