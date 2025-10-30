from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.session import get_async_session
from app.core.security import verify_event_token
from app.models.models import Event, Club
from app.schemas.club import ClubResponse

router = APIRouter(prefix="/api/v1/branding", tags=["branding"])

@router.get("/by-event/{event_token}", response_model=ClubResponse)
async def branding_by_event(event_token: str, db: AsyncSession = Depends(get_async_session)):
    event_id = verify_event_token(event_token)
    ev = (await db.execute(select(Event).where(Event.id==event_id))).scalar_one_or_none()
    if not ev:
        from fastapi import HTTPException
        raise HTTPException(404, "Event not found")
    c = (await db.execute(select(Club).where(Club.id==ev.club_id))).scalar_one()
    return ClubResponse.model_validate(c, from_attributes=True)

@router.get("/by-club/{club_slug}", response_model=ClubResponse)
async def branding_by_club(club_slug: str, db: AsyncSession = Depends(get_async_session)):
    c = (await db.execute(select(Club).where(Club.slug==club_slug))).scalar_one_or_none()
    if not c:
        from fastapi import HTTPException
        raise HTTPException(404, "Club not found")
    return ClubResponse.model_validate(c, from_attributes=True)
