from __future__ import annotations

import hashlib
import hmac
import json
import os
import time
from typing import Any, Dict, Optional
from urllib.parse import parse_qsl

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

router = APIRouter(prefix="/api/v1/auth/telegram", tags=["auth"])

BOT_TOKEN = os.getenv("BOT_TOKEN", "")
JWT_SECRET = os.getenv("JWT_SECRET", "dev_secret_change_me")
JWT_TTL_SECONDS = int(os.getenv("JWT_TTL_SECONDS", "86400"))  # 24h


def _b64url(data: bytes) -> str:
    import base64
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")

def _jwt_encode(payload: dict) -> str:
    header = {"alg": "HS256", "typ": "JWT"}
    import base64
    h = _b64url(json.dumps(header, separators=(",", ":")).encode())
    p = _b64url(json.dumps(payload, separators=(",", ":")).encode())
    sig = hmac.new(JWT_SECRET.encode(), msg=f"{h}.{p}".encode(), digestmod=hashlib.sha256).digest()
    s = _b64url(sig)
    return f"{h}.{p}.{s}"

def verify_webapp_init_data(init_data: str, max_age_seconds: int = 60 * 60) -> dict:
    """
    Telegram WebApp signature verification.
    """
    if not BOT_TOKEN:
        raise HTTPException(500, "BOT_TOKEN is not set")

    pairs = dict(parse_qsl(init_data, keep_blank_values=True))
    their_hash = pairs.pop("hash", None)
    if not their_hash:
        raise HTTPException(401, "Missing hash")

    auth_date = int(pairs.get("auth_date", "0") or 0)
    if auth_date and (int(time.time()) - auth_date) > max_age_seconds:
        raise HTTPException(401, "initData is too old")

    data_check_string = "\n".join(f"{k}={pairs[k]}" for k in sorted(pairs.keys()))
    secret_key = hmac.new(b"WebAppData", BOT_TOKEN.encode(), hashlib.sha256).digest()
    calc_hash = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()

    if not hmac.compare_digest(calc_hash, their_hash):
        raise HTTPException(401, "Bad initData signature")

    user_raw = pairs.get("user")
    user = json.loads(user_raw) if user_raw else None
    if not user or not user.get("id"):
        raise HTTPException(401, "No user in initData")

    return user

class AuthResponse(BaseModel):
    access_token: str
    user: dict


@router.get("/webapp", response_model=AuthResponse)
def webapp_auth(init_data: str = Query(..., alias="init_data")):
    verified = verify_telegram_webapp_init_data(init_data)
    u = verified.get("user") or {}
    tg_id = u.get("id")
    if not tg_id:
        raise HTTPException(401, "No user in initData")

    now = int(time.time())
    token = _jwt_encode({"sub": str(tg_id), "iat": now, "exp": now + JWT_TTL_SECONDS})

    user_payload = {
        "tg_id": tg_id,
        "tg_username": u.get("username"),
        "first_name": u.get("first_name"),
        "last_name": u.get("last_name"),
        "img": u.get("photo_url"),
    }
    return {"access_token": token, "user": user_payload}
