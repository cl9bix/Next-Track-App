from typing import List
from fastapi import HTTPException, status
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from app.models.models import Event, Round, Song, Vote, User
from app.schemas.schemas import StateResponse, EventResponse, RoundResponse, SongResponse
from app.services.live_bus import publish_event


async def get_or_create_user(db: AsyncSession, telegram_id: int) -> User:
    res = await db.execute(select(User).where(User.telegram_id == telegram_id))
    u = res.scalar_one_or_none()
    if u:
        return u
    u = User(telegram_id=telegram_id)
    db.add(u)
    await db.commit()
    await db.refresh(u)
    return u


async def vote_for_song(db: AsyncSession, user: User, song_id: int) -> dict:
    s = (await db.execute(select(Song).where(Song.id == song_id))).scalar_one_or_none()
    if not s:
        raise HTTPException(status_code=404, detail="Song not found")

    v = Vote(user_id=user.id, song_id=song_id)
    db.add(v)
    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        # унікальне обмеження (user_id, song_id)
        raise HTTPException(status.HTTP_409_CONFLICT, detail="Already voted for this song")

    # поточний count для UI
    cnt = await db.execute(select(func.count(Vote.id)).where(Vote.song_id == song_id))
    votes = cnt.scalar_one()
    await publish_event(s.event_id, {"type": "vote", "song_id": song_id, "votes": votes})
    return {"ok": True, "votes": votes}


async def event_state(db: AsyncSession, event_id: int, user: User) -> StateResponse:
    ev = (await db.execute(select(Event).where(Event.id == event_id))).scalar_one_or_none()
    if not ev or not ev.current_round_id:
        raise HTTPException(404, "Event not found or has no active round")

    r = (await db.execute(select(Round).where(Round.id == ev.current_round_id))).scalar_one()

    rows = await db.execute(
        select(Song.id, Song.name, Song.round_id, func.count(Vote.id).label("votes"))
        .join(Vote, Vote.song_id == Song.id, isouter=True)
        .where(Song.round_id == r.id)
        .group_by(Song.id)
        .order_by(func.count(Vote.id).desc(), Song.id.asc())
    )
    songs = [SongResponse(id=i, name=n, round_id=rid, votes=v) for i, n, rid, v in rows.all()]

    my = await db.execute(
        select(Vote.song_id).where(Vote.user_id == user.id)
        .join(Song, Song.id == Vote.song_id)
        .where(Song.round_id == r.id)
    )
    my_ids = [s for (s,) in my.all()]

    return StateResponse(
        event=EventResponse.model_validate(ev, from_attributes=True),
        round=RoundResponse.model_validate(r, from_attributes=True),
        songs=songs,
        user_voted_song_ids=my_ids,
    )
