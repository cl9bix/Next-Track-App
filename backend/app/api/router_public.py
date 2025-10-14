from fastapi import APIRouter, Depends, Header
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.session import get_async_session
from app.core.security import verify_telegram_init_data, verify_event_token
from app.crud.vote_crud import get_or_create_user, event_state, vote_for_song
from app.crud.song_crud import add_song_to_current_round
# (опційно) rate limit / idempotency
# from app.utils.ratelimit import rate_limit, ensure_idempotent

router = APIRouter(prefix="/api/v1/public", tags=["public"])


@router.get("/event/{event_token}/state")
async def get_state(
        event_token: str,
        init_data: str = Header(..., alias="X-Telegram-InitData"),
        db: AsyncSession = Depends(get_async_session),
):
    user_info = verify_telegram_init_data(init_data)     # -> dict with id
    user = await get_or_create_user(db, user_info["id"])
    event_id = verify_event_token(event_token)
    return await event_state(db, event_id, user)


@router.post("/event/{event_token}/songs")
async def suggest_song(
        event_token: str,
        payload: dict,
        init_data: str = Header(..., alias="X-Telegram-InitData"),
        db: AsyncSession = Depends(get_async_session),
):
    verify_telegram_init_data(init_data)
    event_id = verify_event_token(event_token)
    name = (payload.get("name") or "").strip()
    # await rate_limit(f"rl:suggest:{event_id}", 30, 60)   # опц. глобальний RL
    return await add_song_to_current_round(db, event_id, payload={"name": name})


@router.post("/event/{event_token}/vote")
async def vote(
        event_token: str,
        payload: dict,
        init_data: str = Header(..., alias="X-Telegram-InitData"),
        db: AsyncSession = Depends(get_async_session),
):
    user_info = verify_telegram_init_data(init_data)
    user = await get_or_create_user(db, user_info["id"])
    verify_event_token(event_token)
    song_id = int(payload.get("song_id"))
    # await rate_limit(f"rl:vote:{user.id}", 10, 30)
    # await ensure_idempotent(f"idem:vote:{user.id}:{song_id}", 5)
    return await vote_for_song(db, user, song_id)
