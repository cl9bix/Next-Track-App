from typing import Optional, List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException

from app.models.models import Organisator
from pydantic import BaseModel, ConfigDict


class OrganiserCreate(BaseModel):
    name: str
    telegram_id: int | None = None

class OrganiserResponse(BaseModel):
    id: int
    name: str
    telegram_id: int | None = None
    model_config = ConfigDict(from_attributes=True)


async def get_by_telegram(db: AsyncSession, telegram_id: int) -> Optional[OrganiserResponse]:
    res = await db.execute(select(Organisator).where(Organisator.telegram_id == telegram_id))
    o = res.scalar_one_or_none()
    return OrganiserResponse.model_validate(o, from_attributes=True) if o else None


async def create(db: AsyncSession, payload: OrganiserCreate) -> OrganiserResponse:
    o = Organisator(**payload.model_dump())
    db.add(o)
    await db.commit()
    await db.refresh(o)
    return OrganiserResponse.model_validate(o, from_attributes=True)


async def list_all(db: AsyncSession) -> List[OrganiserResponse]:
    res = await db.execute(select(Organisator).order_by(Organisator.id.asc()))
    return [OrganiserResponse.model_validate(o, from_attributes=True) for o in res.scalars().all()]
