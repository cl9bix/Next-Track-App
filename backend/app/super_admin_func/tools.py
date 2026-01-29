from __future__ import annotations
import asyncio

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.session import async_session
from app.models.models import AdminUser, Club
from app.core.auth import hash_password


async def create_admin(
    telegram_id: int,
    display_name: str,
    username: str,
    password_raw: str,
    club_id: int,
    role: str,
):
    async with async_session() as db:
        admin = (
            await db.execute(
                select(AdminUser).where(AdminUser.username == username)
            )
        ).scalar_one_or_none()

        if admin:
            print("❌ Admin already exists")
            return

        admin = AdminUser(
            telegram_id=telegram_id,
            display_name=display_name,
            username=username,
            password_hash=hash_password(password_raw),
            role=role,
            club_id=club_id,
            is_active=True,
        )

        db.add(admin)
        await db.commit()

        print(f"✅ Admin created: {username}")


async def create_club(name: str, slug: str):
    async with async_session() as db:
        club = (
            await db.execute(
                select(Club).where(Club.slug == slug)
            )
        ).scalar_one_or_none()

        if club:
            print("❌ Club already exists")
            return

        club = Club(name=name, slug=slug)
        db.add(club)
        await db.commit()

        print(f"✅ Club created: {name}")


async def main():
    action = int(input("1: Create admin\n2: Create club\nAction = "))

    if action == 1:
        await create_admin(
            telegram_id=int(input("Telegram ID: ")),
            display_name=input("Display name: "),
            username=input("Username: "),
            password_raw=input("Password: "),
            club_id=int(input("Club ID: ")),
            role=input("Role (owner/admin): "),
        )

    elif action == 2:
        await create_club(
            name=input("Club name: "),
            slug=input("Slug: "),
        )


if __name__ == "__main__":
    asyncio.run(main())
