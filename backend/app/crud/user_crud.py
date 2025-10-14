from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException

from app.models.models import User
from app.schemas.schemas import ConfigDict
from pydantic import BaseModel


class UserResponse(BaseModel):
    id: int
    telegram_id: int
    notifications: bool
    model_config = ConfigDict(from_attributes=True)


async def get_user(db: AsyncSession, user_id: int) -> UserResponse:
    res = await db.execute(select(User).where(User.id == user_id))
    u = res.scalar_one_or_none()
    if not u:
        raise HTTPException(404, "User not found")
    return UserResponse.model_validate(u, from_attributes=True)


async def list_users(db: AsyncSession) -> List[UserResponse]:
    res = await db.execute(select(User).order_by(User.id.asc()))
    return [UserResponse.model_validate(u, from_attributes=True) for u in res.scalars().all()]


async def get_or_create_by_telegram(db: AsyncSession, telegram_id: int) -> UserResponse:
    res = await db.execute(select(User).where(User.telegram_id == telegram_id))
    u = res.scalar_one_or_none()
    if not u:
        u = User(telegram_id=telegram_id)
        db.add(u)
        await db.commit()
        await db.refresh(u)
    return UserResponse.model_validate(u, from_attributes=True)


async def set_notifications(db: AsyncSession, user_id: int, enabled: bool) -> UserResponse:
    res = await db.execute(select(User).where(User.id == user_id))
    u = res.scalar_one_or_none()
    if not u:
        raise HTTPException(404, "User not found")
    u.notifications = enabled
    await db.commit()
    return UserResponse.model_validate(u, from_attributes=True)
