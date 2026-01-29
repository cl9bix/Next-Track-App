from __future__ import annotations

import os
import datetime as dt
from typing import Optional

from fastapi import Depends, HTTPException, Request, status
from jose import jwt, JWTError
from passlib.context import CryptContext
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.session import get_async_session as get_db
from app.models.models import AdminUser

PWD = CryptContext(schemes=["bcrypt"], deprecated="auto")

ADMIN_JWT_SECRET = os.getenv("ADMIN_JWT_SECRET", os.getenv("SECRET_KEY", "dev-secret-change-me"))
ADMIN_JWT_ALG = "HS256"
ADMIN_JWT_EXPIRES_MIN = int(os.getenv("ADMIN_JWT_EXPIRES_MIN", "720"))  # 12 год


def hash_password(password: str) -> str:
    return PWD.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    return PWD.verify(password, password_hash)


def create_admin_token(admin: AdminUser) -> str:
    exp = dt.datetime.now(dt.timezone.utc) + dt.timedelta(minutes=ADMIN_JWT_EXPIRES_MIN)
    payload = {
        "sub": str(admin.id),
        "club_id": admin.club_id,
        "role": getattr(admin, "role", None),
        "exp": exp,
    }
    return jwt.encode(payload, ADMIN_JWT_SECRET, algorithm=ADMIN_JWT_ALG)


def _extract_token(request: Request) -> Optional[str]:
    # 1) cookie
    t = request.cookies.get("admin_token")
    if t:
        return t

    # 2) Authorization: Bearer
    auth = request.headers.get("Authorization", "")
    if auth.startswith("Bearer "):
        return auth.split(" ", 1)[1].strip()

    return None


async def get_current_admin(
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> AdminUser:
    token = _extract_token(request)
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

    try:
        data = jwt.decode(token, ADMIN_JWT_SECRET, algorithms=[ADMIN_JWT_ALG])
        admin_id = int(data.get("sub"))
    except (JWTError, ValueError):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    admin = (await db.execute(
        select(AdminUser).where(AdminUser.id == admin_id, AdminUser.is_active == True)
    )).scalar_one_or_none()

    if not admin:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Admin not found")

    return admin
