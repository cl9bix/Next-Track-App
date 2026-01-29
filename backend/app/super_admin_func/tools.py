from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional, List

from fastapi import APIRouter, Depends, Form, HTTPException, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.session import get_async_session as get_db
from app.models.models import AdminUser, Club, Event, Dj, EventDJ
from app.core.auth import verify_password, create_admin_token, get_current_admin,hash_password
from watchfiles import awatch


async def main():
    action = int(input("1: Create admin\n2: Create club\nAction="))
    if action == 1:
        telegram_id=input("Enter tg_id=")
        display_name=input("Enter display_name=")
        username=input("Enter username=")
        password_rare=input("Enter password_rare=")
        club_id=int(input("Enter club_id="))
        role=input("Enter role=")
        await create_admin(telegram_id, display_name, username, password_rare, club_id, role)
    elif action ==2:
        name = input("Enter club's name=")
        slug = input("Enter slug=")
        await create_club(name, slug)


async def create_admin(telegram_id,display_name,username,password_rare,club_id,role,db: AsyncSession = Depends(get_db)):
    admin = (await db.execute(
        select(AdminUser).where(AdminUser.username == username)
    )).scalar_one_or_none()

    if admin:
        return "Admin already exsists"
    add_admin = AdminUser(
        telegram_id=telegram_id,
        display_name=display_name,
        username=username,
        password= hash_password(password_rare),
        role=role,
        is_active=True,
    )
    db.add(add_admin)
    await db.commit()
    await db.refresh(add_admin)
    return f"Successfully added: data:\n{add_admin}"


async def create_club(name:str,slug:str,db: AsyncSession = Depends(get_db)):
    club = (await db.execute(
        select(Club).where(Club.slug == slug)
    )).scalar_one_or_none()

    if club:
        return "Club already exsists"
    add_club = Club(
        name=name,
        slug=slug
    )
    db.add(add_club)
    await db.commit()
    await db.refresh(add_club)
    return f"Successfully added: data:\n{add_club}"



if __name__ =='__main__':
    print(main())



