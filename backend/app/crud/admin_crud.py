from typing import Optional, List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException

from app.models.models import AdminUser,AdminClub,Club
from pydantic import BaseModel, ConfigDict



async def _admin_me_payload(db: AsyncSession, admin: AdminUser) -> dict:
    club_links = (
        await db.execute(
            select(AdminClub, Club)
            .join(Club, Club.id == AdminClub.club_id)
            .where(AdminClub.admin_id == admin.id)
        )
    ).all()

    clubs = [
        {
            "id": club.id,
            "name": club.name,
            "slug": club.slug,
        }
        for _, club in club_links
    ]

    return {
        "id": admin.id,
        "username": admin.username,
        "display_name": admin.display_name,
        "telegram_id": admin.telegram_id,
        "role": getattr(getattr(admin, "role", None), "value", getattr(admin, "role", None)),
        "is_active": admin.is_active,
        "max_club_count": admin.max_club_count,
        "clubs": clubs,
    }