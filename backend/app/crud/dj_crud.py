from typing import Optional, List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException

from app.models.models import Dj
from pydantic import BaseModel, ConfigDict


class DjCreate(BaseModel):
    name: str
    telegram_id: int

class DjResponse(BaseModel):
    id: int
    name: str
    telegram_id: int
    model_config = ConfigDict(from_attributes=True)


async def get_by_telegram(db: AsyncSession, telegram_id: int) -> Optional[DjResponse]:
    res = await db.execute(select(Dj).where(Dj.telegram_id == telegram_id))
    d = res.scalar_one_or_none()
    return DjResponse.model_validate(d, from_attributes=True) if d else None


async def create(db: AsyncSession, payload: DjCreate) -> DjResponse:
    d = Dj(**payload.model_dump())
    db.add(d)
    await db.commit()
    await db.refresh(d)
    return DjResponse.model_validate(d, from_attributes=True)


async def list_all(db: AsyncSession) -> List[DjResponse]:
    res = await db.execute(select(Dj).order_by(Dj.id.asc()))
    return [DjResponse.model_validate(d, from_attributes=True) for d in res.scalars().all()]
