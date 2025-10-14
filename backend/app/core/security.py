import base64, hashlib, hmac, json, time, urllib.parse
from fastapi import HTTPException, status
from app.core.config import settings

# ---- Telegram WebApp initData verification ----
def verify_telegram_init_data(init_data: str) -> dict:
    data = dict(urllib.parse.parse_qsl(init_data, keep_blank_values=True))
    tg_hash = data.pop("hash", None)
    if not tg_hash:
        raise HTTPException(400, "Missing Telegram hash")

    check_string = "\n".join(f"{k}={data[k]}" for k in sorted(data.keys()))
    secret_key = hashlib.sha256(settings.BOT_TOKEN.encode()).digest()
    calc = hmac.new(secret_key, check_string.encode(), hashlib.sha256).hexdigest()
    if not hmac.compare_digest(calc, tg_hash):
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Invalid Telegram initData")

    try:
        auth_date = int(data.get("auth_date", "0"))
        if time.time() - auth_date > 60 * 60 * 24:
            raise HTTPException(status.HTTP_403_FORBIDDEN, "initData expired")
    except ValueError:
        pass

    user = json.loads(data.get("user", "{}") or "{}")
    if "id" not in user:
        raise HTTPException(400, "Telegram user missing")
    return user

# ---- Signed Event Token: base64url(payload) + '.' + HMAC ----
def sign_event_token(event_id: int, ttl_seconds: int = 60*60*24) -> str:
    payload = {"e": event_id, "exp": int(time.time()) + ttl_seconds}
    raw = json.dumps(payload, separators=(",", ":"), ensure_ascii=False).encode()
    sig = hmac.new(settings.EVENT_TOKEN_SECRET.encode(), raw, hashlib.sha256).digest()
    return base64.urlsafe_b64encode(raw).decode().rstrip("=") + "." + base64.urlsafe_b64encode(sig).decode().rstrip("=")

def verify_event_token(token: str) -> int:
    try:
        p_enc, s_enc = token.split(".", 1)
        raw = base64.urlsafe_b64decode(p_enc + "==")
        sig = base64.urlsafe_b64decode(s_enc + "==")
        calc = hmac.new(settings.EVENT_TOKEN_SECRET.encode(), raw, hashlib.sha256).digest()
        if not hmac.compare_digest(calc, sig):
            raise HTTPException(status.HTTP_403_FORBIDDEN, "Invalid event token")
        data = json.loads(raw.decode())
        if data.get("exp", 0) < int(time.time()):
            raise HTTPException(status.HTTP_403_FORBIDDEN, "Event token expired")
        return int(data["e"])
    except Exception:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Bad event token")
