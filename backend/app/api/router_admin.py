from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from pydantic import BaseModel, Field
from sqlalchemy import delete, desc, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.schemas.schemas import ClubSettingsUpdate

from app.models.session import get_async_session as get_db
from app.models.models import (
    AdminUser,
    AdminRole,
    Club,
    Event,
    Dj,
    EventDJ,
    AdminClub,
    ClubSettings,

)
from app.core.auth import (
    verify_password,
    create_admin_token,
    get_current_admin,
    hash_password,
)

router = APIRouter(prefix="/api/v1/admin", tags=["admin-api"])


# =========================
# SCHEMAS
# =========================
class AdminLoginIn(BaseModel):
    username: str
    password: str


class AdminRegisterIn(BaseModel):
    username: str
    password: str
    display_name: Optional[str] = None
    telegram_id: Optional[int] = None
    club_id: int
    role: str = "admin"


class AdminClubOut(BaseModel):
    id: int
    name: str
    slug: str


class AdminMeOut(BaseModel):
    id: int
    username: str
    display_name: Optional[str] = None
    telegram_id: Optional[int] = None
    role: str
    is_active: bool
    max_club_count: int
    clubs: list[AdminClubOut] = Field(default_factory=list)


class AdminDashboardAdminOut(BaseModel):
    id: int
    username: str
    display_name: Optional[str] = None
    telegram_id: Optional[int] = None
    role: str
    club_id: int
    is_active: bool


class EventCreateIn(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    preview: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    dj_ids: list[int] = Field(default_factory=list)


class EventUpdateIn(BaseModel):
    title: Optional[str] = Field(default=None, min_length=1, max_length=255)
    preview: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    dj_ids: Optional[list[int]] = None


class EventOut(BaseModel):
    id: int
    club_id: int
    title: str
    preview: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    created_at: datetime
    dj_ids: list[int] = Field(default_factory=list)


class DashboardOut(BaseModel):
    admin: AdminDashboardAdminOut
    club: AdminClubOut
    total_events: int
    live_events: int
    upcoming_events: int
    recent_events: list[EventOut]


# =========================
# HELPERS
# =========================
def _normalize_dt(dt: Optional[datetime]) -> Optional[datetime]:
    if dt is None:
        return None
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def _calc_event_status(ev: Event) -> str:
    now = datetime.now(timezone.utc)
    start = _normalize_dt(ev.start_date)
    end = _normalize_dt(ev.end_date)

    if end and now > end:
        return "ended"
    if start and now >= start and (not end or now <= end):
        return "live"
    return "scheduled"


def _admin_role_value(admin: AdminUser) -> str:
    return getattr(getattr(admin, "role", None), "value", getattr(admin, "role", "admin"))


async def _get_admin_clubs(db: AsyncSession, admin_id: int) -> list[Club]:
    result = await db.execute(
        select(Club)
        .join(AdminClub, AdminClub.club_id == Club.id)
        .where(AdminClub.admin_id == admin_id)
        .order_by(Club.id.asc())
    )
    return list(result.scalars().all())


def _club_to_dict(club: Club) -> dict:
    return {
        "id": club.id,
        "name": club.name,
        "slug": club.slug,
    }


def _admin_me_to_dict(admin: AdminUser, clubs: list[Club]) -> dict:
    return {
        "id": admin.id,
        "username": admin.username,
        "display_name": admin.display_name,
        "telegram_id": admin.telegram_id,
        "role": _admin_role_value(admin),
        "is_active": admin.is_active,
        "max_club_count": getattr(admin, "max_club_count", 1),
        "clubs": [_club_to_dict(club) for club in clubs],
    }


def _dashboard_admin_to_dict(admin: AdminUser, club_id: int) -> dict:
    return {
        "id": admin.id,
        "username": admin.username,
        "display_name": admin.display_name,
        "telegram_id": admin.telegram_id,
        "role": _admin_role_value(admin),
        "club_id": club_id,
        "is_active": admin.is_active,
    }


async def _event_dj_ids(db: AsyncSession, event_id: int) -> list[int]:
    rows = (
        await db.execute(select(EventDJ.dj_id).where(EventDJ.event_id == event_id))
    ).scalars().all()
    return list(rows)


async def _event_to_dict(db: AsyncSession, event: Event) -> dict:
    return {
        "id": event.id,
        "club_id": event.club_id,
        "title": event.title,
        "preview": event.preview,
        "start_date": event.start_date,
        "end_date": event.end_date,
        "created_at": event.created_at,
        "dj_ids": await _event_dj_ids(db, event.id),
    }


async def _resolve_selected_club(
        db: AsyncSession,
        admin: AdminUser,
        club_id: Optional[int],
) -> Club:
    clubs = await _get_admin_clubs(db, admin.id)

    if not clubs:
        raise HTTPException(status_code=403, detail="Admin has no assigned clubs")

    if club_id is None:
        return clubs[0]

    for club in clubs:
        if club.id == club_id:
            return club

    raise HTTPException(status_code=403, detail="You do not have access to this club")


async def _get_owned_event(db: AsyncSession, event_id: int, club_id: int) -> Event:
    event = (
        await db.execute(
            select(Event).where(
                Event.id == event_id,
                Event.club_id == club_id,
                )
        )
    ).scalar_one_or_none()

    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    return event


async def _validate_dj_ids(db: AsyncSession, dj_ids: list[int]) -> list[int]:
    unique_ids = sorted(set(dj_ids))
    if not unique_ids:
        return []

    found_ids = set(
        (
            await db.execute(
                select(Dj.id).where(Dj.id.in_(unique_ids))
            )
        ).scalars().all()
    )

    missing = [dj_id for dj_id in unique_ids if dj_id not in found_ids]
    if missing:
        raise HTTPException(
            status_code=404,
            detail=f"DJ not found: {missing}",
        )

    return unique_ids


def _clean_optional_text(value: Optional[str]) -> Optional[str]:
    if value is None:
        return None
    stripped = value.strip()
    return stripped or None


def _validate_event_dates(
        start_date: Optional[datetime],
        end_date: Optional[datetime],
) -> None:
    start = _normalize_dt(start_date)
    end = _normalize_dt(end_date)

    if start and end and end < start:
        raise HTTPException(
            status_code=400,
            detail="end_date must be greater than or equal to start_date",
        )


# =========================
# AUTH
# =========================
@router.post("/login")
async def admin_login(
        payload: AdminLoginIn,
        response: Response,
        db: AsyncSession = Depends(get_db),
):
    username = payload.username.strip()

    admin = (
        await db.execute(
            select(AdminUser).where(AdminUser.username == username)
        )
    ).scalar_one_or_none()

    if not admin or not admin.is_active or not verify_password(payload.password, admin.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_admin_token(admin)
    clubs = await _get_admin_clubs(db, admin.id)

    response.set_cookie(
        "admin_token",
        token,
        httponly=True,
        samesite="lax",
        secure=False,  # під https -> True
        max_age=60 * 60 * 12,
        path="/",
    )

    return {
        "status": "success",
        "access_token": token,
        "token_type": "bearer",
        "admin": _admin_me_to_dict(admin, clubs),
    }


@router.post("/register", response_model=AdminMeOut, status_code=status.HTTP_201_CREATED)
async def admin_register(
        payload: AdminRegisterIn,
        response: Response,
        db: AsyncSession = Depends(get_db),
):
    username = payload.username.strip()
    password = payload.password.strip()

    if not username or not password:
        raise HTTPException(status_code=400, detail="Username and password are required")

    existing = (
        await db.execute(select(AdminUser).where(AdminUser.username == username))
    ).scalar_one_or_none()
    if existing:
        raise HTTPException(status_code=409, detail="Username already exists")

    club = (
        await db.execute(select(Club).where(Club.id == payload.club_id))
    ).scalar_one_or_none()
    if not club:
        raise HTTPException(status_code=404, detail="Club not found")

    try:
        parsed_role = AdminRole(payload.role) if payload.role in ("owner", "admin") else AdminRole.admin
    except Exception:
        parsed_role = AdminRole.admin

    admin = AdminUser(
        username=username,
        password_hash=hash_password(password),
        display_name=_clean_optional_text(payload.display_name),
        telegram_id=payload.telegram_id,
        role=parsed_role,
        is_active=True,
        max_club_count=1,
    )

    db.add(admin)
    await db.flush()

    db.add(AdminClub(admin_id=admin.id, club_id=payload.club_id))
    await db.commit()
    await db.refresh(admin)

    token = create_admin_token(admin)
    response.set_cookie(
        "admin_token",
        token,
        httponly=True,
        samesite="lax",
        secure=False,
        max_age=60 * 60 * 12,
        path="/",
    )

    clubs = await _get_admin_clubs(db, admin.id)
    return AdminMeOut(**_admin_me_to_dict(admin, clubs))


@router.post("/logout")
async def admin_logout(response: Response):
    response.delete_cookie("admin_token", path="/")
    return {"status": "success"}


@router.get("/me", response_model=AdminMeOut)
async def admin_me(
        me: AdminUser = Depends(get_current_admin),
        db: AsyncSession = Depends(get_db),
):
    clubs = await _get_admin_clubs(db, me.id)
    return AdminMeOut(**_admin_me_to_dict(me, clubs))


# =========================
# DASHBOARD
# =========================
@router.get("/dashboard", response_model=DashboardOut)
async def dashboard(
        club_id: Optional[int] = Query(default=None),
        me: AdminUser = Depends(get_current_admin),
        db: AsyncSession = Depends(get_db),
):
    club = await _resolve_selected_club(db, me, club_id)

    events = (
        await db.execute(
            select(Event)
            .where(Event.club_id == club.id)
            .order_by(desc(Event.start_date).nullslast(), desc(Event.id))
        )
    ).scalars().all()

    live_events = 0
    upcoming_events = 0

    for event in events:
        event_status = _calc_event_status(event)
        if event_status == "live":
            live_events += 1
        elif event_status == "scheduled":
            upcoming_events += 1

    recent_events = [EventOut(**(await _event_to_dict(db, event))) for event in events[:10]]

    return DashboardOut(
        admin=AdminDashboardAdminOut(**_dashboard_admin_to_dict(me, club.id)),
        club=AdminClubOut(**_club_to_dict(club)),
        total_events=len(events),
        live_events=live_events,
        upcoming_events=upcoming_events,
        recent_events=recent_events,
    )


# =========================
# EVENTS
# =========================
@router.get("/events", response_model=list[EventOut])
async def list_events(
        club_id: Optional[int] = Query(default=None),
        me: AdminUser = Depends(get_current_admin),
        db: AsyncSession = Depends(get_db),
):
    club = await _resolve_selected_club(db, me, club_id)

    events = (
        await db.execute(
            select(Event)
            .where(Event.club_id == club.id)
            .order_by(desc(Event.start_date).nullslast(), desc(Event.id))
        )
    ).scalars().all()

    return [EventOut(**(await _event_to_dict(db, event))) for event in events]


@router.post("/events", response_model=EventOut, status_code=status.HTTP_201_CREATED)
async def create_event(
        payload: EventCreateIn,
        club_id: Optional[int] = Query(default=None),
        me: AdminUser = Depends(get_current_admin),
        db: AsyncSession = Depends(get_db),
):
    club = await _resolve_selected_club(db, me, club_id)

    clean_title = payload.title.strip()
    if not clean_title:
        raise HTTPException(status_code=400, detail="Title is required")

    _validate_event_dates(payload.start_date, payload.end_date)
    valid_dj_ids = await _validate_dj_ids(db, payload.dj_ids)

    event = Event(
        club_id=club.id,
        title=clean_title,
        preview=_clean_optional_text(payload.preview),
        start_date=payload.start_date,
        end_date=payload.end_date,
    )
    db.add(event)
    await db.flush()

    for dj_id in valid_dj_ids:
        db.add(EventDJ(event_id=event.id, dj_id=dj_id))

    await db.commit()
    await db.refresh(event)

    return EventOut(**(await _event_to_dict(db, event)))


@router.get("/events/{event_id}", response_model=EventOut)
async def get_event(
        event_id: int,
        club_id: Optional[int] = Query(default=None),
        me: AdminUser = Depends(get_current_admin),
        db: AsyncSession = Depends(get_db),
):
    club = await _resolve_selected_club(db, me, club_id)
    event = await _get_owned_event(db, event_id, club.id)
    return EventOut(**(await _event_to_dict(db, event)))


@router.patch("/events/{event_id}", response_model=EventOut)
async def update_event(
        event_id: int,
        payload: EventUpdateIn,
        club_id: Optional[int] = Query(default=None),
        me: AdminUser = Depends(get_current_admin),
        db: AsyncSession = Depends(get_db),
):
    club = await _resolve_selected_club(db, me, club_id)
    event = await _get_owned_event(db, event_id, club.id)

    next_start_date = payload.start_date if payload.start_date is not None else event.start_date
    next_end_date = payload.end_date if payload.end_date is not None else event.end_date
    _validate_event_dates(next_start_date, next_end_date)

    if payload.title is not None:
        clean_title = payload.title.strip()
        if not clean_title:
            raise HTTPException(status_code=400, detail="Title cannot be empty")
        event.title = clean_title

    if payload.preview is not None:
        event.preview = _clean_optional_text(payload.preview)

    if payload.start_date is not None:
        event.start_date = payload.start_date

    if payload.end_date is not None:
        event.end_date = payload.end_date

    if payload.dj_ids is not None:
        valid_dj_ids = await _validate_dj_ids(db, payload.dj_ids)

        await db.execute(
            delete(EventDJ).where(EventDJ.event_id == event.id)
        )
        for dj_id in valid_dj_ids:
            db.add(EventDJ(event_id=event.id, dj_id=dj_id))

    await db.commit()
    await db.refresh(event)

    return EventOut(**(await _event_to_dict(db, event)))


@router.post("/events/{event_id}/end")
async def end_event(
        event_id: int,
        club_id: Optional[int] = Query(default=None),
        me: AdminUser = Depends(get_current_admin),
        db: AsyncSession = Depends(get_db),
):
    club = await _resolve_selected_club(db, me, club_id)
    event = await _get_owned_event(db, event_id, club.id)

    event.end_date = datetime.now(timezone.utc)
    await db.commit()
    await db.refresh(event)

    return {
        "status": "success",
        "event_id": event.id,
        "end_date": event.end_date.isoformat() if event.end_date else None,
    }


@router.delete("/events/{event_id}")
async def delete_event(
        event_id: int,
        club_id: Optional[int] = Query(default=None),
        me: AdminUser = Depends(get_current_admin),
        db: AsyncSession = Depends(get_db),
):
    club = await _resolve_selected_club(db, me, club_id)
    event = await _get_owned_event(db, event_id, club.id)

    await db.execute(delete(EventDJ).where(EventDJ.event_id == event.id))
    await db.delete(event)
    await db.commit()

    return {
        "status": "success",
        "deleted_id": event_id,
    }


@router.get("/club-settings")
async def get_club_settings(
        club_id: Optional[int] = Query(default=None),
        me: AdminUser = Depends(get_current_admin),
        db: AsyncSession = Depends(get_db),
):
    club = await _resolve_selected_club(db, me, club_id)

    settings = (
        await db.execute(
            select(ClubSettings).where(ClubSettings.club_id == club.id)
        )
    ).scalar_one_or_none()

    return {
        "club": {
            "id": club.id,
            "name": club.name,
            "slug": club.slug,
        },
        "settings": {
            "description": settings.description if settings else None,
            "background_image_url": settings.background_image_url if settings else None,
            "max_suggestions_per_user": settings.max_suggestions_per_user if settings else 3,
            "voting_duration_sec": settings.voting_duration_sec if settings else 60,
            "allow_explicit": settings.allow_explicit if settings else False,
            "auto_play": settings.auto_play if settings else False,
        },
    }



@router.patch("/club-settings")
async def update_club_settings(
        payload: ClubSettingsUpdate,
        club_id: Optional[int] = Query(default=None),
        me: AdminUser = Depends(get_current_admin),
        db: AsyncSession = Depends(get_db),
):
    club = await _resolve_selected_club(db, me, club_id)

    settings = (
        await db.execute(
            select(ClubSettings).where(ClubSettings.club_id == club.id)
        )
    ).scalar_one_or_none()

    if not settings:
        settings = ClubSettings(club_id=club.id)
        db.add(settings)
        await db.flush()

    if payload.name is not None:
        club.name = payload.name.strip()

    if payload.description is not None:
        settings.description = payload.description

    if payload.max_suggestions_per_user is not None:
        settings.max_suggestions_per_user = payload.max_suggestions_per_user

    if payload.voting_duration_sec is not None:
        settings.voting_duration_sec = payload.voting_duration_sec

    if payload.allow_explicit is not None:
        settings.allow_explicit = payload.allow_explicit

    if payload.auto_play is not None:
        settings.auto_play = payload.auto_play

    if payload.background_image_url is not None:
        settings.background_image_url = payload.background_image_url.strip() or None
    await db.commit()

    return {"status": "success"}