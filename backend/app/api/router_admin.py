from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, Form, HTTPException, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.session import get_async_session as get_db
from app.models.models import AdminUser, Club, Event, Dj, EventDJ
from app.core.auth import verify_password, create_admin_token, get_current_admin

router = APIRouter(prefix="/admin", tags=["admin"])
templates = Jinja2Templates(directory="templates")


# =========================
# HELPERS
# =========================
def _parse_dt(s: str) -> Optional[datetime]:
    s = (s or "").strip()
    if not s:
        return None
    s = s.replace("T", " ")
    dt = datetime.fromisoformat(s)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt


def admin_to_dict(a: AdminUser) -> dict:
    return {
        "id": a.id,
        "username": getattr(a, "username", None),
        "display_name": getattr(a, "display_name", None),
        "telegram_id": getattr(a, "telegram_id", None),
        "role": getattr(getattr(a, "role", None), "value", getattr(a, "role", None)),
        "club_id": getattr(a, "club_id", None),
        "is_active": getattr(a, "is_active", None),
        "created_at": a.created_at.isoformat() if getattr(a, "created_at", None) else None,
    }


def club_to_dict(c: Club) -> dict:
    return {
        "id": c.id,
        "name": c.name,
        "slug": c.slug,
    }


def event_to_dict(e: Event) -> dict:
    # якщо треба JS на фронті — зручно мати
    return {
        "id": e.id,
        "club_id": e.club_id,
        "title": e.title,
        "preview": e.preview,
        "start_date": e.start_date.isoformat() if e.start_date else None,
        "end_date": e.end_date.isoformat() if e.end_date else None,
        "created_at": e.created_at.isoformat() if e.created_at else None,
    }


# =========================
# PAGES
# =========================
@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request, "error": None})


@router.post("/login")
async def admin_login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    db: AsyncSession = Depends(get_db),
):
    admin = (
        await db.execute(select(AdminUser).where(AdminUser.username == username))
    ).scalar_one_or_none()

    if not admin or not admin.is_active or not verify_password(password, admin.password_hash):
        return templates.TemplateResponse(
            "login.html",
            {"request": request, "error": "Invalid credentials"},
            status_code=status.HTTP_401_UNAUTHORIZED,
        )

    token = create_admin_token(admin)

    resp = RedirectResponse(url="/admin/", status_code=303)
    resp.set_cookie(
        "admin_token",
        token,
        httponly=True,
        samesite="lax",
        secure=True,  # якщо локально без https — постав False
        max_age=60 * 60 * 12,
        path="/",
    )
    return resp


@router.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    """
    Заглушка під твій future-flow.
    Якщо треба реально “тільки для George” — зробимо IP allowlist + basic password.
    """
    return templates.TemplateResponse("register.html", {"request": request, "error": None})


@router.get("/logout")
async def admin_logout():
    resp = RedirectResponse(url="/admin/login", status_code=303)
    resp.delete_cookie("admin_token", path="/")
    return resp


@router.get("/", response_class=HTMLResponse)
async def dashboard(
    request: Request,
    me: AdminUser = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    club = (
        await db.execute(select(Club).where(Club.id == me.club_id))
    ).scalar_one_or_none()
    if not club:
        raise HTTPException(404, "Club not found")

    events = (
        await db.execute(
            select(Event)
            .where(Event.club_id == me.club_id)
            .order_by(desc(Event.start_date).nullslast(), desc(Event.id))
        )
    ).scalars().all()

    # важливо: в шаблон — dict, щоб можна було робити |tojson
    admin_dict = admin_to_dict(me)
    club_dict = club_to_dict(club)
    events_dict = [event_to_dict(e) for e in events]

    return templates.TemplateResponse(
        "admin_dashboard.html",
        {
            "request": request,
            "admin": admin_dict,
            "club": club_dict,
            "events": events,           # якщо рендериш Jinja циклом
            "events_json": events_dict, # якщо треба в JS: {{ events_json|tojson }}
        },
    )


@router.get("/events/new", response_class=HTMLResponse)
async def new_event_form(
    request: Request,
    me: AdminUser = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    djs = (await db.execute(select(Dj).order_by(Dj.name.asc()))).scalars().all()
    return templates.TemplateResponse(
        "create_event.html",
        {"request": request, "admin": admin_to_dict(me), "djs": djs, "error": None},
    )


@router.post("/events/new")
async def create_event(
    request: Request,
    title: str = Form(...),
    preview: str = Form(""),
    start_date: str = Form(""),
    end_date: str = Form(""),
    dj_ids: Optional[str] = Form(None),  # CSV: "1,2,3"
    me: AdminUser = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    try:
        sd = _parse_dt(start_date)
        ed = _parse_dt(end_date)
    except Exception:
        djs = (await db.execute(select(Dj).order_by(Dj.name.asc()))).scalars().all()
        return templates.TemplateResponse(
            "create_event.html",
            {
                "request": request,
                "admin": admin_to_dict(me),
                "djs": djs,
                "error": "Invalid date format (YYYY-MM-DD HH:MM or ISO)",
            },
            status_code=400,
        )

    clean_title = title.strip()
    if not clean_title:
        djs = (await db.execute(select(Dj).order_by(Dj.name.asc()))).scalars().all()
        return templates.TemplateResponse(
            "admin_event_new.html",
            {"request": request, "admin": admin_to_dict(me), "djs": djs, "error": "Title is required"},
            status_code=400,
        )

    ev = Event(
        club_id=me.club_id,
        title=clean_title,
        preview=(preview.strip() or None),
        start_date=sd,
        end_date=ed,
    )
    db.add(ev)
    await db.commit()
    await db.refresh(ev)

    # прив'язка DJ до івенту
    if dj_ids:
        ids = [int(x) for x in dj_ids.split(",") if x.strip().isdigit()]
        # уникнемо дубляжу
        ids = list(dict.fromkeys(ids))
        for dj_id in ids:
            db.add(EventDJ(event_id=ev.id, dj_id=dj_id))
        await db.commit()

    return RedirectResponse(url="/admin/", status_code=303)


@router.post("/events/{event_id}/end")
async def end_event(
    event_id: int,
    me: AdminUser = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    ev = (
        await db.execute(
            select(Event).where(Event.id == event_id, Event.club_id == me.club_id)
        )
    ).scalar_one_or_none()

    if not ev:
        raise HTTPException(404, "Event not found")

    ev.end_date = datetime.now(timezone.utc)
    await db.commit()
    return RedirectResponse(url="/admin/", status_code=303)
