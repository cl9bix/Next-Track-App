# app/routers/search.py
from fastapi import APIRouter, Query, Header
from typing import Optional
from app.services.music_search import unified_search

router = APIRouter(prefix="/api", tags=["search"])

@router.get("/search")
async def search_tracks(
        q: str = Query(..., min_length=2, max_length=120),
        limit: int = Query(15, ge=1, le=50),
        accept_language: Optional[str] = Header(default=None, alias="Accept-Language"),
):
    """
    Глобальний пошук треків (Deezer → iTunes fallback).
    Повертає { items: [{ id, title, artist, album, cover_url }] }.
    """
    result = await unified_search(q=q, limit=limit, lang=accept_language)
    return result
