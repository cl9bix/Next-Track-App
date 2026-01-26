from __future__ import annotations

import base64
import hashlib
import hmac
import json
import os
import time
from fastapi import Header, HTTPException

JWT_SECRET = os.getenv("JWT_SECRET", "dev_secret_change_me")


def _b64url_decode(s: str) -> bytes:
    s += "=" * (-len(s) % 4)
    return base64.urlsafe_b64decode(s.encode())

def require_user(authorization: str | None = Header(default=None)) -> int:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(401, "Missing token")
    token = authorization.split(" ", 1)[1].strip()
    parts = token.split(".")
    if len(parts) != 3:
        raise HTTPException(401, "Bad token")
    h, p, sig = parts
    expected = hmac.new(JWT_SECRET.encode(), msg=f"{h}.{p}".encode(), digestmod=hashlib.sha256).digest()
    if not hmac.compare_digest(expected, _b64url_decode(sig)):
        raise HTTPException(401, "Bad signature")

    payload = json.loads(_b64url_decode(p))
    if int(payload.get("exp", 0)) < int(time.time()):
        raise HTTPException(401, "Token expired")
    return int(payload["sub"])
