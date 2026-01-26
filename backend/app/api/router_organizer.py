from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.session import get_async_session
from app.core.security import verify_telegram_init_data, sign_event_token
from app.models.models import Organisator, Event
from app.schemas.schemas import EventCreate, EventUpdate, EventResponse, RoundResponse
from app.crud.event_crud import (
    create_event, update_event, delete_event, list_events, get_event,
    current_round, end_round_and_start_next
)

from app.crud import organisator_crud
from app.schemas.schemas import OrganisatorCreate, OrganisatorResponse

router = APIRouter(prefix="/api/v1/organisator", tags=["organisator"])


async def require_organizer(
        init_data: str = Header(..., alias="X-Telegram-InitData"),
        db: AsyncSession = Depends(get_async_session),
) -> Organisator:
    user = verify_telegram_init_data(init_data)
    r = await db.execute(select(Organisator).where(Organisator.telegram_id == user["id"]))
    org = r.scalar_one_or_none()
    if not org:
        raise HTTPException(
            403,
            detail=("Щоб виставити свою улюблену пісню на голосування, відскануйте QR у клубі. "
                    "Якщо ви зацікавлені в інтеграції — напишіть @cl9bix."),
        )
    return org


@router.post("/", response_model=OrganisatorResponse, status_code=201)
async def create_organisator(payload: OrganisatorCreate, db: AsyncSession = Depends(get_async_session)):
    return await organisator_crud.create_organisator(db, payload)


@router.get('/all', response_model=OrganisatorResponse, status_code=200)
async def all_organisators(db: AsyncSession = Depends(get_async_session)):
    return await organisator_crud.list_all(db)


@router.get("/events", response_model=list[EventResponse])
async def events(org: Organisator = Depends(require_organizer),
                 db: AsyncSession = Depends(get_async_session)):
    return await list_events(db)


@router.post("/events", response_model=EventResponse)
async def create_event_ep(payload: EventCreate,
                          org: Organisator = Depends(require_organizer),
                          db: AsyncSession = Depends(get_async_session)):
    payload.organisator_id = org.id  # type: ignore[attr-defined]
    return await create_event(db, payload)


@router.get("/events/{event_id}", response_model=EventResponse)
async def get_event_ep(event_id: int,
                       org: Organisator = Depends(require_organizer),
                       db: AsyncSession = Depends(get_async_session)):
    return await get_event(db, event_id)


@router.patch("/events/{event_id}", response_model=EventResponse)
async def update_event_ep(event_id: int, payload: EventUpdate,
                          org: Organisator = Depends(require_organizer),
                          db: AsyncSession = Depends(get_async_session)):
    return await update_event(db, event_id, payload)


@router.delete("/events/{event_id}")
async def delete_event_ep(event_id: int,
                          org: Organisator = Depends(require_organizer),
                          db: AsyncSession = Depends(get_async_session)):
    await delete_event(db, event_id)
    return {"ok": True}


@router.get("/events/{event_id}/qr")
async def get_qr(event_id: int, org: Organisator = Depends(require_organizer)):
    token = sign_event_token(event_id)
    return {"event_id": event_id, "deep_link": f"https://t.me/next_track_bot?start=event_{token}"}


@router.get("/events/{event_id}/current-round", response_model=RoundResponse)
async def get_current_round(event_id: int,
                            org: Organisator = Depends(require_organizer),
                            db: AsyncSession = Depends(get_async_session)):
    return await current_round(db, event_id)


@router.post("/events/{event_id}/rounds/end")
async def end_round(event_id: int,
                    org: Organisator = Depends(require_organizer),
                    db: AsyncSession = Depends(get_async_session)):
    return await end_round_and_start_next(db, event_id)
