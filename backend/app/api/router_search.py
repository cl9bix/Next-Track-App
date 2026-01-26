from fastapi import APIRouter, Request
from app.services.music_search import unified_search

router = APIRouter(tags=["search"])

@router.get("/search")
async def search(request: Request, q: str, limit: int = 15):
    lang = request.headers.get("Accept-Language")
    return await unified_search(q=q, limit=limit, lang=lang)
