from __future__ import annotations

import os
import base64
import hashlib
import datetime as dt
from typing import Optional

from fastapi import Depends, HTTPException, Request, status
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.session import get_async_session as get_db
from app.models.models import AdminUser


PWD = CryptContext(schemes=["bcrypt"], deprecated="auto")

ADMIN_JWT_SECRET = os.getenv(
    "ADMIN_JWT_SECRET",
    os.getenv("SECRET_KEY", "dev-secret-change-me"),
)
ADMIN_JWT_ALG = "HS256"
ADMIN_JWT_EXPIRES_MIN = int(os.getenv("ADMIN_JWT_EXPIRES_MIN", "720"))


def _normalize_password(password: str) -> str:
    """
    bcrypt works reliably only up to 72 bytes.
    Pre-hash the raw password with SHA-256 and convert to stable ASCII.
    """
    digest = hashlib.sha256(password.encode("utf-8")).digest()
    return base64.b64encode(digest).decode("ascii")


def hash_password(password: str) -> str:
    normalized = _normalize_password(password)
    return PWD.hash(normalized)


def verify_password(password: str, password_hash: str) -> bool:
    normalized = _normalize_password(password)
    return PWD.verify(normalized, password_hash)


def _get_admin_role_value(admin: AdminUser) -> str:
    return getattr(getattr(admin, "role", None), "value", getattr(admin, "role", "admin"))


def create_admin_token(admin: AdminUser) -> str:
    now = dt.datetime.now(dt.timezone.utc)
    exp = now + dt.timedelta(minutes=ADMIN_JWT_EXPIRES_MIN)

    payload = {
        "sub": str(admin.id),
        "role": _get_admin_role_value(admin),
        "type": "admin",
        "iat": now,
        "exp": exp,
    }

    return jwt.encode(payload, ADMIN_JWT_SECRET, algorithm=ADMIN_JWT_ALG)


def _extract_token(request: Request) -> Optional[str]:
    cookie_token = request.cookies.get("admin_token")
    if cookie_token:
        return cookie_token

    auth_header = request.headers.get("Authorization", "")
    if auth_header.startswith("Bearer "):
        return auth_header.split(" ", 1)[1].strip()

    return None


async def get_current_admin(
        request: Request,
        db: AsyncSession = Depends(get_db),
) -> AdminUser:
    token = _extract_token(request)
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )

    try:
        payload = jwt.decode(token, ADMIN_JWT_SECRET, algorithms=[ADMIN_JWT_ALG])

        token_type = payload.get("type")
        if token_type != "admin":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type",
            )

        admin_id_raw = payload.get("sub")
        admin_id = int(admin_id_raw)
    except (JWTError, ValueError, TypeError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )

    admin = (
        await db.execute(
            select(AdminUser).where(
                AdminUser.id == admin_id,
                AdminUser.is_active.is_(True),
                )
        )
    ).scalar_one_or_none()

    if not admin:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Admin not found",
        )

    return admin