from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException
from app.models.models import Club
from app.schemas.club import ClubCreate, ClubUpdate, ClubResponse

def to_resp(c: Club) -> ClubResponse:
    return ClubResponse.model_validate(c, from_attributes=True)

async def create(db: AsyncSession, payload: ClubCreate) -> ClubResponse:
    c = Club(**payload.model_dump())
    db.add(c); await db.commit(); await db.refresh(c)
    return to_resp(c)

async def update(db: AsyncSession, club_id: int, payload: ClubUpdate) -> ClubResponse:
    c = (await db.execute(select(Club).where(Club.id==club_id))).scalar_one_or_none()
    if not c: raise HTTPException(404, "Club not found")
    data = payload.model_dump(exclude_unset=True)
    for k,v in data.items(): setattr(c,k,v)
    await db.commit(); await db.refresh(c)
    return to_resp(c)

async def get_by_slug(db: AsyncSession, slug: str) -> ClubResponse:
    c = (await db.execute(select(Club).where(Club.slug==slug))).scalar_one_or_none()
    if not c: raise HTTPException(404, "Club not found")
    return to_resp(c)

async def get_by_tg_username(db: AsyncSession, username: str) -> ClubResponse:
    c = (await db.execute(select(Club).where(Club.tg_username==username))).scalar_one_or_none()
    if not c: raise HTTPException(404, "Club not found")
    return to_resp(c)
