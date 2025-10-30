from typing import Optional, List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException

from app.models.models import Organisator
from pydantic import BaseModel, ConfigDict
from app.schemas.schemas import OrganisatorCreate,OrganisatorResponse
from app.core.auth import hash_password



async def get_by_telegram(db: AsyncSession, telegram_id: int) -> Optional[OrganisatorCreate]:
    res = await db.execute(select(Organisator).where(Organisator.telegram_id == telegram_id))
    o = res.scalar_one_or_none()
    return OrganisatorCreate.model_validate(o, from_attributes=True) if o else None


async def create_organisator(db: AsyncSession, payload: OrganisatorCreate) -> OrganisatorCreate:
    org = Organisator(
        name=payload.name,
        username=payload.username,
        telegram_id=payload.telegram_id,
        password_hash=hash_password(payload.password),
    )
    db.add(org)
    await db.commit()
    await db.refresh(org)
    return OrganisatorCreate.model_validate(o, from_attributes=True)


async def list_all(db: AsyncSession) -> List[OrganisatorCreate]:
    res = await db.execute(select(Organisator).order_by(Organisator.id.asc()))
    return [OrganisatorCreate.model_validate(o, from_attributes=True) for o in res.scalars().all()]
