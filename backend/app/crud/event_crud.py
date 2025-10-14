from typing import List, Optional

from fastapi import HTTPException, status
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.models import Event, Round
from app.schemas.schemas import EventCreate, EventUpdate, EventResponse, RoundResponse
from app.services.live_bus import publish_event


def to_event(e: Event) -> EventResponse:
    return EventResponse.model_validate(e, from_attributes=True)


async def list_events(db: AsyncSession) -> List[EventResponse]:
    res = await db.execute(
        select(Event).order_by(Event.start_date.is_(None), Event.start_date.asc(), Event.id.asc())
    )
    return [to_event(e) for e in res.scalars().all()]


async def get_event(db: AsyncSession, event_id: int) -> EventResponse:
    res = await db.execute(select(Event).where(Event.id == event_id))
    e = res.scalar_one_or_none()
    if not e:
        raise HTTPException(status_code=404, detail="Event not found")
    return to_event(e)


async def create_event(db: AsyncSession, payload: EventCreate) -> EventResponse:
    e = Event(**payload.model_dump(exclude_unset=True))
    db.add(e)
    await db.commit()
    await db.refresh(e)

    # перший раунд
    r = Round(event_id=e.id, number=1)
    db.add(r)
    await db.commit()
    await db.refresh(r)

    e.current_round_id = r.id
    await db.commit()
    await db.refresh(e)
    return to_event(e)


async def update_event(db: AsyncSession, event_id: int, payload: EventUpdate) -> EventResponse:
    res = await db.execute(select(Event).where(Event.id == event_id))
    e: Optional[Event] = res.scalar_one_or_none()
    if not e:
        raise HTTPException(status_code=404, detail="Event not found")

    data = payload.model_dump(exclude_unset=True)
    for k, v in data.items():
        setattr(e, k, v)
    await db.commit()
    await db.refresh(e)
    return to_event(e)


async def delete_event(db: AsyncSession, event_id: int) -> None:
    res = await db.execute(select(Event).where(Event.id == event_id))
    e = res.scalar_one_or_none()
    if not e:
        raise HTTPException(status_code=404, detail="Event not found")
    await db.delete(e)
    await db.commit()


# ---- Раунд-менеджмент для організатора ----

async def current_round(db: AsyncSession, event_id: int) -> RoundResponse:
    ev = (await db.execute(select(Event).where(Event.id == event_id))).scalar_one_or_none()
    if not ev or not ev.current_round_id:
        raise HTTPException(404, "Event or round not found")
    r = (await db.execute(select(Round).where(Round.id == ev.current_round_id))).scalar_one()
    return RoundResponse.model_validate(r, from_attributes=True)


async def end_round_and_start_next(db: AsyncSession, event_id: int) -> dict:
    ev = (await db.execute(select(Event).where(Event.id == event_id))).scalar_one_or_none()
    if not ev or not ev.current_round_id:
        raise HTTPException(404, "Event or round not found")

    cur = (await db.execute(select(Round).where(Round.id == ev.current_round_id))).scalar_one()

    # визначаємо переможця по кількості голосів
    from app.models.models import Song, Vote
    res = await db.execute(
        select(Song.id, func.count(Vote.id).label("v"))
        .join(Vote, Vote.song_id == Song.id, isouter=True)
        .where(Song.round_id == cur.id)
        .group_by(Song.id)
        .order_by(func.count(Vote.id).desc())
        .limit(1)
    )
    row = res.first()
    cur.winner_song_id = row[0] if row else None
    cur.ended_at = func.now()
    await db.commit()
    await db.refresh(cur)

    # стартуємо новий раунд
    nxt = Round(event_id=event_id, number=cur.number + 1)
    db.add(nxt)
    await db.commit()
    await db.refresh(nxt)

    ev.current_round_id = nxt.id
    await db.commit()
    await db.refresh(ev)

    payload = {
        "type": "round_ended",
        "winner_song_id": cur.winner_song_id,
        "ended_round_id": cur.id,
        "new_round_id": nxt.id,
        "new_round_number": nxt.number,
    }
    await publish_event(event_id, payload)
    return payload
