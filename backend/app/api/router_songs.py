from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.session import get_async_session
from app.crud.song_crud import list_songs_in_current_round, delete_song
from app.schemas.schemas import SongResponse

router = APIRouter(prefix="/api/v1/songs", tags=["songs"])

@router.get("/event/{event_id}/current", response_model=list[SongResponse])
async def list_current_round_songs(event_id: int, db: AsyncSession = Depends(get_async_session)):
    return await list_songs_in_current_round(db, event_id)

@router.delete("/{song_id}")
async def delete_song_ep(song_id: int, db: AsyncSession = Depends(get_async_session)):
    await delete_song(db, song_id)
    return {"ok": True}
