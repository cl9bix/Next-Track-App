# app/services/music_search.py
from __future__ import annotations
import time
from typing import Any, Dict, List, Optional
import httpx
from functools import lru_cache

SEARCH_TTL_SECONDS = 60

# Примітивний кеш у пам'яті: key -> (ts, payload)
_cache: Dict[str, tuple[float, dict]] = {}

def cache_get(key: str) -> Optional[dict]:
    rec = _cache.get(key)
    if not rec:
        return None
    ts, payload = rec
    if time.time() - ts > SEARCH_TTL_SECONDS:
        _cache.pop(key, None)
        return None
    return payload

def cache_put(key: str, payload: dict) -> None:
    _cache[key] = (time.time(), payload)

def _pick_first(*vals):
    for v in vals:
        if v is None:
            continue
        if isinstance(v, str) and v.strip() == "":
            continue
        return v
    return ""

def _normalize_one(item: dict) -> dict:
    """
    Зводимо будь-який трек до формату фронту.
    """
    # Deezer
    if "artist" in item and "album" in item and "title" in item:
        return {
            "id": str(item.get("id") or item.get("track_id") or item.get("link") or ""),
            "title": item.get("title") or "",
            "artist": _pick_first(item.get("artist", {}).get("name")),
            "album": _pick_first(item.get("album", {}).get("title")),
            "cover_url": _pick_first(
                item.get("album", {}).get("cover_xl"),
                item.get("album", {}).get("cover_big"),
                item.get("album", {}).get("cover_medium"),
                item.get("album", {}).get("cover")
            ) or "",
        }
    # iTunes
    if "trackId" in item and "trackName" in item:
        return {
            "id": str(item.get("trackId")),
            "title": item.get("trackName") or "",
            "artist": item.get("artistName") or "",
            "album": item.get("collectionName") or "",
            "cover_url": _pick_first(item.get("artworkUrl100"), item.get("artworkUrl60")) or "",
        }
    # Гнучкий fallback
    return {
        "id": str(_pick_first(item.get("id"), item.get("trackId"), item.get("key"), item.get("link"), "")),
        "title": _pick_first(item.get("title"), item.get("name"), item.get("trackName"), item.get("label"), "") or "Untitled",
        "artist": _pick_first(item.get("artist"), item.get("artistName"), item.get("author"), ""),
        "album": _pick_first(item.get("album"), item.get("albumName"), item.get("collectionName"), ""),
        "cover_url": _pick_first(item.get("cover_url"), item.get("thumbnail"), item.get("artworkUrl100"), ""),
    }

async def search_deezer(q: str, limit: int, lang: str | None) -> List[dict]:
    # Документація: https://developers.deezer.com/api/search
    url = "https://api.deezer.com/search"
    params = {"q": q, "limit": max(1, min(limit, 50))}
    headers = {"Accept": "application/json"}
    if lang:
        headers["Accept-Language"] = lang
    async with httpx.AsyncClient(timeout=httpx.Timeout(8.0)) as client:
        r = await client.get(url, params=params, headers=headers)
        r.raise_for_status()
        data = r.json()
    raw = data.get("data") or []
    return [_normalize_one(x) for x in raw]

async def search_itunes(q: str, limit: int, lang: str | None) -> List[dict]:
    # Документація: https://developer.apple.com/library/archive/documentation/AudioVideo/Conceptual/iTuneSearchAPI/
    url = "https://itunes.apple.com/search"
    params = {"term": q, "entity": "song", "limit": max(1, min(limit, 50))}
    headers = {"Accept": "application/json"}
    if lang:
        headers["Accept-Language"] = lang
    async with httpx.AsyncClient(timeout=httpx.Timeout(8.0)) as client:
        r = await client.get(url, params=params, headers=headers)
        r.raise_for_status()
        data = r.json()
    raw = data.get("results") or []
    return [_normalize_one(x) for x in raw]

async def unified_search(q: str, limit: int, lang: Optional[str]) -> dict:
    """
    Спочатку намагаємось Deezer, якщо мало — добираємо iTunes.
    """
    key = f"search:{lang or ''}:{q}|{limit}"
    cached = cache_get(key)
    if cached:
        return cached

    items: List[dict] = []
    try:
        items = await search_deezer(q, limit, lang)
    except Exception:
        items = []

    if len(items) < limit:
        try:
            extra = await search_itunes(q, limit, lang)
            # мердж без дублів за (title, artist)
            seen = set((i["title"].lower(), (i["artist"] or "").lower()) for i in items)
            for it in extra:
                key2 = (it["title"].lower(), (it["artist"] or "").lower())
                if key2 not in seen:
                    items.append(it)
                    seen.add(key2)
                if len(items) >= limit:
                    break
        except Exception:
            pass

    resp = {"items": items[:limit]}
    cache_put(key, resp)
    return resp
