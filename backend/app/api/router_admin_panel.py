from __future__ import annotations

from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.session import get_async_session as get_db
from app.models.models import AdminUser, Club, Event
from app.api.auth_telegram_webapp import verify_webapp_init_data

router = APIRouter(prefix="/admin", tags=["admin"])
templates = Jinja2Templates(directory="templates")


# --- helper: read initData from cookie or header ---
def _get_init_data(request: Request) -> Optional[str]:
    return request.cookies.get("tg_init") or request.headers.get("X-Telegram-InitData")


async def require_admin(request: Request, db: AsyncSession = Depends(get_db)) -> AdminUser:
    init_data = _get_init_data(request)
    if not init_data:
        raise HTTPException(401, "Telegram auth required")

    user = verify_webapp_init_data(init_data)
    tg_id = int(user["id"])

    q = select(AdminUser).where(AdminUser.telegram_id == tg_id, AdminUser.is_active == True)
    admin = (await db.execute(q)).scalar_one_or_none()
    if not admin:
        raise HTTPException(403, "Admin not allowed")

    # optional: fill display_name once
    if not admin.display_name:
        admin.display_name = user.get("username") or user.get("first_name") or "admin"
        await db.commit()

    return admin


@router.post("/session")
async def admin_session(request: Request):
    """
    JS з адмінки викликає це, передає initData, ми ставимо cookie tg_init.
    """
    data = await request.json()
    init_data = (data or {}).get("init_data") or ""
    # одразу валідуємо, щоб не зберігати сміття
    verify_webapp_init_data(init_data)

    resp = JSONResponse({"ok": True})
    # samesite=None потрібен, якщо домен/вбудований браузер вередує (ngrok), але інколи вистачає "lax".
    resp.set_cookie("tg_init", init_data, httponly=True, samesite="lax")
    return resp


@router.get("", response_class=HTMLResponse)
async def dashboard(request: Request, admin: AdminUser = Depends(require_admin), db: AsyncSession = Depends(get_db)):
    club = (await db.execute(select(Club).where(Club.id == admin.club_id))).scalar_one()
    events = (await db.execute(
        select(Event).where(Event.club_id == club.id).order_by(desc(Event.start_date).nullslast(), desc(Event.id))
    )).scalars().all()

    return templates.TemplateResponse(
        "admin_dashboard.html",
        {"request": request, "admin": admin, "club": club, "events": events},
    )


@router.get("/events/new", response_class=HTMLResponse)
async def new_event_form(request: Request, admin: AdminUser = Depends(require_admin), db: AsyncSession = Depends(get_db)):
    club = (await db.execute(select(Club).where(Club.id == admin.club_id))).scalar_one()
    return templates.TemplateResponse("admin_event_new.html", {"request": request, "club": club})


def _parse_dt(val: str) -> Optional[datetime]:
    val = (val or "").strip()
    if not val:
        return None
    # HTML datetime-local -> "YYYY-MM-DDTHH:MM"
    try:
        return datetime.fromisoformat(val)
    except Exception:
        return None


@router.post("/events/new")
async def create_event(
        request: Request,
        title: str = Form(...),
        preview: str = Form(""),
        start_date: str = Form(""),
        end_date: str = Form(""),
        admin: AdminUser = Depends(require_admin),
        db: AsyncSession = Depends(get_db),
):
    club_id = admin.club_id

    ev = Event(
        club_id=club_id,
        title=title.strip(),
        preview=(preview.strip() or None),
        start_date=_parse_dt(start_date),
        end_date=_parse_dt(end_date),
    )
    db.add(ev)
    await db.commit()

    return RedirectResponse(url="/admin", status_code=303)
