from typing import List
from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.models import Round, Event
from app.schemas.schemas import RoundResponse


def to_round(r: Round) -> RoundResponse:
    return RoundResponse.model_validate(r, from_attributes=True)


async def list_rounds(db: AsyncSession, event_id: int) -> List[RoundResponse]:
    res = await db.execute(select(Round).where(Round.event_id == event_id).order_by(Round.number.asc()))
    return [to_round(r) for r in res.scalars().all()]


async def get_round(db: AsyncSession, round_id: int) -> RoundResponse:
    res = await db.execute(select(Round).where(Round.id == round_id))
    r = res.scalar_one_or_none()
    if not r:
        raise HTTPException(404, "Round not found")
    return to_round(r)


async def set_current_round(db: AsyncSession, event_id: int, round_id: int) -> RoundResponse:
    ev = (await db.execute(select(Event).where(Event.id == event_id))).scalar_one_or_none()
    if not ev:
        raise HTTPException(404, "Event not found")

    r = (await db.execute(select(Round).where(Round.id == round_id, Round.event_id == event_id))).scalar_one_or_none()
    if not r:
        raise HTTPException(404, "Round not found for event")

    ev.current_round_id = r.id
    await db.commit()
    return to_round(r)
