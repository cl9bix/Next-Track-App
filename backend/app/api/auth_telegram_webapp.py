from __future__ import annotations

import base64
import hashlib
import hmac
import json
import os
import time
from typing import Any, Dict

from urllib.parse import parse_qsl

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel


router = APIRouter(prefix="/api/v1/auth/telegram", tags=["auth"])

# Telegram bot token (required)
BOT_TOKEN = os.getenv("BOT_TOKEN", "").strip()

# JWT signing secret (required in prod)
JWT_SECRET = os.getenv("JWT_SECRET", "dev_secret_change_me").strip()

# 24h default
JWT_TTL_SECONDS = int(os.getenv("JWT_TTL_SECONDS", "86400"))


def _b64url(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


def _jwt_encode(payload: dict) -> str:
    """
    Minimal HS256 JWT encoder without external deps.
    """
    header = {"alg": "HS256", "typ": "JWT"}
    h = _b64url(json.dumps(header, separators=(",", ":"), ensure_ascii=False).encode("utf-8"))
    p = _b64url(json.dumps(payload, separators=(",", ":"), ensure_ascii=False).encode("utf-8"))

    signing_input = f"{h}.{p}".encode("utf-8")
    sig = hmac.new(JWT_SECRET.encode("utf-8"), msg=signing_input, digestmod=hashlib.sha256).digest()
    s = _b64url(sig)
    return f"{h}.{p}.{s}"


def verify_webapp_init_data(init_data: str, max_age_seconds: int = 60 * 60) -> Dict[str, Any]:
    """
    Telegram WebApp signature verification.

    Returns: Telegram user dict (the JSON from init_data['user'])
    """
    if not BOT_TOKEN:
        raise HTTPException(status_code=500, detail="BOT_TOKEN is not set")

    pairs = dict(parse_qsl(init_data, keep_blank_values=True))

    their_hash = pairs.pop("hash", None)
    if not their_hash:
        raise HTTPException(status_code=401, detail="Missing hash")

    # optional freshness check
    auth_date_raw = pairs.get("auth_date", "0") or "0"
    try:
        auth_date = int(auth_date_raw)
    except ValueError:
        raise HTTPException(status_code=401, detail="Bad auth_date")

    if auth_date and (int(time.time()) - auth_date) > max_age_seconds:
        raise HTTPException(status_code=401, detail="initData is too old")

    # data_check_string
    data_check_string = "\n".join(f"{k}={pairs[k]}" for k in sorted(pairs.keys()))

    secret_key = hmac.new(b"WebAppData", BOT_TOKEN.encode("utf-8"), hashlib.sha256).digest()
    calc_hash = hmac.new(secret_key, data_check_string.encode("utf-8"), hashlib.sha256).hexdigest()

    if not hmac.compare_digest(calc_hash, their_hash):
        raise HTTPException(status_code=401, detail="Bad initData signature")

    user_raw = pairs.get("user")
    if not user_raw:
        raise HTTPException(status_code=401, detail="No user in initData")

    try:
        user = json.loads(user_raw)
    except Exception:
        raise HTTPException(status_code=401, detail="Bad user JSON in initData")

    if not user or not user.get("id"):
        raise HTTPException(status_code=401, detail="No user id in initData")

    return user


class AuthResponse(BaseModel):
    access_token: str
    user: dict


@router.get("/webapp", response_model=AuthResponse)
def webapp_auth(init_data: str = Query(..., alias="init_data")):
    # verify_webapp_init_data returns USER DICT directly
    u = verify_webapp_init_data(init_data)

    tg_id = u.get("id")
    if not tg_id:
        raise HTTPException(status_code=401, detail="No user in initData")

    now = int(time.time())
    token = _jwt_encode(
        {
            "sub": str(tg_id),
            "tg_id": int(tg_id),
            "username": u.get("username"),
            "iat": now,
            "exp": now + JWT_TTL_SECONDS,
        }
    )

    user_payload = {
        "tg_id": tg_id,
        "tg_username": u.get("username"),
        "first_name": u.get("first_name"),
        "last_name": u.get("last_name"),
        "img": u.get("photo_url"),
    }

    return {"access_token": token, "user": user_payload}
