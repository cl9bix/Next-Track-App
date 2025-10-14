from typing import List
from fastapi import HTTPException, status
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.models import Event, Round, Song, Vote
from app.schemas.schemas import SongCreate, SongResponse
from app.services.live_bus import publish_event


def to_song(id: int, name: str, round_id: int, votes: int) -> SongResponse:
    return SongResponse(id=id, name=name, round_id=round_id, votes=votes)


async def add_song_to_current_round(db: AsyncSession, event_id: int, payload: SongCreate) -> SongResponse:
    ev = (await db.execute(select(Event).where(Event.id == event_id))).scalar_one_or_none()
    if not ev or not ev.current_round_id:
        raise HTTPException(404, "Event not found or has no active round")

    s = Song(name=payload.name.strip(), event_id=event_id, round_id=ev.current_round_id)
    db.add(s)
    try:
        await db.commit()
    except Exception as e:
        await db.rollback()
        # імовірно зловили UniqueConstraint (однакова назва в раунді)
        raise HTTPException(status.HTTP_409_CONFLICT, detail="Song already exists in current round") from e
    await db.refresh(s)

    await publish_event(event_id, {"type": "song_added", "song": {"id": s.id, "name": s.name, "round_id": s.round_id}})
    return to_song(s.id, s.name, s.round_id, votes=0)


async def list_songs_in_current_round(db: AsyncSession, event_id: int) -> List[SongResponse]:
    ev = (await db.execute(select(Event).where(Event.id == event_id))).scalar_one_or_none()
    if not ev or not ev.current_round_id:
        raise HTTPException(404, "Event not found or has no active round")

    rows = await db.execute(
        select(Song.id, Song.name, Song.round_id, func.count(Vote.id).label("votes"))
        .join(Vote, Vote.song_id == Song.id, isouter=True)
        .where(Song.round_id == ev.current_round_id)
        .group_by(Song.id)
        .order_by(func.count(Vote.id).desc(), Song.id.asc())
    )
    return [to_song(i, n, rid, v) for i, n, rid, v in rows.all()]


async def delete_song(db: AsyncSession, song_id: int) -> None:
    s = (await db.execute(select(Song).where(Song.id == song_id))).scalar_one_or_none()
    if not s:
        raise HTTPException(404, "Song not found")
    await db.delete(s)
    await db.commit()
