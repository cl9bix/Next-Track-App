from __future__ import annotations

import asyncio
import time
from typing import Dict, List, Optional, Tuple
import httpx

SEARCH_TTL_SECONDS = 45  # короткий TTL => свіжо і швидко
MAX_LIMIT = 25          # для autocomplete цього з головою

# ---------- In-memory cache ----------
_cache: Dict[str, Tuple[float, dict]] = {}
_inflight: Dict[str, asyncio.Task] = {}

def _now() -> float:
    return time.time()

def cache_get(key: str) -> Optional[dict]:
    rec = _cache.get(key)
    if not rec:
        return None
    ts, payload = rec
    if _now() - ts > SEARCH_TTL_SECONDS:
        _cache.pop(key, None)
        return None
    return payload

def cache_put(key: str, payload: dict) -> None:
    _cache[key] = (_now(), payload)

# ---------- Global shared HTTP client (KEEP-ALIVE) ----------
# Важливо: створюємо 1 раз і перевикористовуємо (максимальний буст швидкості)
_TIMEOUT = httpx.Timeout(connect=1.5, read=2.5, write=2.0, pool=2.0)
_LIMITS = httpx.Limits(max_connections=50, max_keepalive_connections=20, keepalive_expiry=30.0)

_client = httpx.AsyncClient(
    timeout=_TIMEOUT,
    limits=_LIMITS,
    headers={"Accept": "application/json"},
)

async def close_http_client() -> None:
    await _client.aclose()

# ---------- Normalize helpers ----------
def _pick_first(*vals):
    for v in vals:
        if v is None:
            continue
        if isinstance(v, str) and v.strip() == "":
            continue
        return v
    return ""

def _safe_int(x, default=0) -> int:
    try:
        return int(x)
    except Exception:
        return default

def _norm_deezer(item: dict) -> dict:
    # Deezer: duration in seconds
    return {
        "id": f"deezer:{item.get('id')}",
        "title": item.get("title") or "",
        "artist": _pick_first((item.get("artist") or {}).get("name")),
        "album": _pick_first((item.get("album") or {}).get("title")),
        "cover_url": _pick_first(
            (item.get("album") or {}).get("cover_xl"),
            (item.get("album") or {}).get("cover_big"),
            (item.get("album") or {}).get("cover_medium"),
            (item.get("album") or {}).get("cover"),
        ) or "",
        "duration_sec": _safe_int(item.get("duration"), 0),
        "source": "deezer",
    }

def _norm_itunes(item: dict) -> dict:
    # iTunes: trackTimeMillis
    return {
        "id": f"itunes:{item.get('trackId')}",
        "title": item.get("trackName") or "",
        "artist": item.get("artistName") or "",
        "album": item.get("collectionName") or "",
        "cover_url": _pick_first(item.get("artworkUrl100"), item.get("artworkUrl60")) or "",
        "duration_sec": max(0, _safe_int(item.get("trackTimeMillis"), 0) // 1000),
        "source": "itunes",
    }

def _dedupe_key(t: dict) -> Tuple[str, str]:
    return (t.get("title", "").strip().lower(), (t.get("artist") or "").strip().lower())

# ---------- Providers ----------
async def search_deezer(q: str, limit: int, lang: Optional[str]) -> List[dict]:
    # https://developers.deezer.com/api/search
    url = "https://api.deezer.com/search"
    params = {"q": q, "limit": max(1, min(limit, 50))}
    headers = {}
    if lang:
        headers["Accept-Language"] = lang

    r = await _client.get(url, params=params, headers=headers)
    r.raise_for_status()
    data = r.json()
    raw = data.get("data") or []
    out = []
    for x in raw:
        try:
            out.append(_norm_deezer(x))
        except Exception:
            continue
    return out

async def search_itunes(q: str, limit: int, lang: Optional[str]) -> List[dict]:
    # https://developer.apple.com/library/archive/documentation/AudioVideo/Conceptual/iTuneSearchAPI/
    url = "https://itunes.apple.com/search"
    params = {"term": q, "entity": "song", "limit": max(1, min(limit, 50))}
    headers = {}
    if lang:
        headers["Accept-Language"] = lang

    r = await _client.get(url, params=params, headers=headers)
    r.raise_for_status()
    data = r.json()
    raw = data.get("results") or []
    out = []
    for x in raw:
        try:
            out.append(_norm_itunes(x))
        except Exception:
            continue
    return out

# ---------- Unified fast search ----------
async def _unified_search_impl(q: str, limit: int, lang: Optional[str]) -> dict:
    q = (q or "").strip()
    limit = max(1, min(int(limit or 10), MAX_LIMIT))
    if len(q) < 2:
        return {"items": []}

    # 1) паралельно стартуємо 2 провайдера
    t1 = asyncio.create_task(search_deezer(q, limit, lang))
    t2 = asyncio.create_task(search_itunes(q, limit, lang))

    items: List[dict] = []
    seen = set()

    # 2) беремо результати у міру готовності (найшвидший перший)
    for fut in asyncio.as_completed([t1, t2], timeout=2):
        try:
            res = await fut
        except Exception:
            res = []

        for it in res:
            k = _dedupe_key(it)
            if k in seen:
                continue
            seen.add(k)
            if not it.get("duration_sec"):
                it["duration_sec"] = 0
            items.append(it)
            if len(items) >= limit:
                # вже досить — гасимо інші таски якщо ще живі
                if not t1.done():
                    t1.cancel()
                if not t2.done():
                    t2.cancel()
                return {"items": items[:limit]}

    return {"items": items[:limit]}

async def unified_search(q: str, limit: int, lang: Optional[str]) -> dict:
    """
    Максимально швидко:
    - cache
    - in-flight dedupe (один запит на key навіть якщо 100 юзерів друкують одночасно)
    - паралельний Deezer+iTunes
    - early stop
    """
    key = f"s:{lang or ''}:{q.strip().lower()}|{min(int(limit or 10), MAX_LIMIT)}"
    cached = cache_get(key)
    if cached:
        return cached

    # in-flight dedupe
    task = _inflight.get(key)
    if task and not task.done():
        return await task

    task = asyncio.create_task(_unified_search_impl(q, limit, lang))
    _inflight[key] = task

    try:
        resp = await task
        cache_put(key, resp)
        return resp
    finally:
        # cleanup inflight
        if _inflight.get(key) is task:
            _inflight.pop(key, None)
