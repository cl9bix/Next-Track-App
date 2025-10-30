# backend/app/main.py
from fastapi import (
    FastAPI, APIRouter, Depends, Header, HTTPException, Request, Response, status, Form
)
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc

from app.models.session import Base, engine, get_async_session as get_db
from app.models.models import Organisator, Event, Club  # Club потрібен для admin-панелі
from app.schemas.schemas import (
    OrganisatorCreate, OrganisatorResponse,
    LoginIn,
    EventCreate, EventResponse as EventOut
)
from app.core.auth import (
    hash_password, verify_password, create_token, get_current_organisator
)
from app.core.security import verify_telegram_init_data  # для guard під WebApp

# API роутери
from app.api.router_public import router as public_router
from app.api.router_organizer import router as organizer_router
from app.api.router_events import router as events_router
from app.api.router_rounds import router as rounds_router
from app.api.router_songs import router as songs_router
from app.api.router_users import router as users_router
from app.api.router_djs import router as djs_router
from app.api.router_ws import router as ws_router
from app.api.router_search import router as search_router  # якщо є

app = FastAPI(title="Next Track API")

# ---- Підключення API роутерів
app.include_router(public_router)
app.include_router(organizer_router)
app.include_router(events_router)
app.include_router(rounds_router)
app.include_router(songs_router)
app.include_router(users_router)
app.include_router(djs_router)
app.include_router(ws_router)
app.include_router(search_router)

# ---- CORS
# УВАГА: allow_credentials=True не можна разом з "*" у origins.
ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5500",
    "http://localhost:5500",
    "https://9c199927d497.ngrok-free.app",  # ← твій ngrok
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---- Статика/шаблони
# Переконайся, що каталоги існують (templates/, static/)
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


@app.get("/health")
async def health():
    return {"ok": True}


# ---------- PAGES ----------
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("user.html", {"request": request})

@app.get("/organisator/", response_class=HTMLResponse)
async def organisator_home(request: Request):
    return templates.TemplateResponse("organisator.html", {"request": request})


# ---------- ORGANISATOR AUTH ----------
@app.post("/organisator/signup", response_model=OrganisatorResponse, status_code=201)
async def organisator_signup(payload: OrganisatorCreate, db: AsyncSession = Depends(get_db)):
    # унікальний username
    q = select(Organisator).where(Organisator.username == payload.username)
    res = await db.execute(q)
    exists = res.scalar_one_or_none()
    if exists:
        raise HTTPException(status_code=409, detail="Username already exists")

    org = Organisator(
        name=payload.name,
        username=payload.username,
        telegram_id=payload.telegram_id,
        password_hash=hash_password(payload.password),
    )
    db.add(org)
    await db.commit()
    await db.refresh(org)
    return org

@app.post("/organisator/login")
async def organisator_login(payload: LoginIn, response: Response, db: AsyncSession = Depends(get_db)):
    q = select(Organisator).where(Organisator.username == payload.username)
    res = await db.execute(q)
    org = res.scalar_one_or_none()
    if not org or not verify_password(payload.password, org.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    token = create_token(org)
    response.set_cookie("org_token", token, httponly=True, samesite="lax")
    return {
        "access_token": token,
        "token_type": "bearer",
        "organisator": {"id": org.id, "name": org.name, "username": org.username}
    }

@app.post("/organisator/logout", status_code=204)
async def organisator_logout(response: Response):
    response.delete_cookie("org_token")
    return Response(status_code=204)

# ВАЖЛИВО: у Depends треба передавати саму функцію, без виклику.
@app.get("/organisator/me", response_model=OrganisatorResponse)
async def organisator_me(current=Depends(get_current_organisator)):
    return current


# ---------- EVENTS (scoped to current organisator) ----------
@app.get("/organisator/events", response_model=list[EventOut])
async def my_events(
        db: AsyncSession = Depends(get_db),
        current=Depends(get_current_organisator),
):
    q = select(Event).where(Event.organisator_id == current.id).order_by(desc(Event.id))
    res = await db.execute(q)
    return res.scalars().all()

@app.post("/organisator/events", response_model=EventOut, status_code=201)
async def create_event_ep(
        payload: EventCreate,
        db: AsyncSession = Depends(get_db),
        current=Depends(get_current_organisator),
):
    ev = Event(
        title=payload.title,
        preview=payload.preview,
        start_date=payload.start_date,
        end_date=payload.end_date,
        dj_id=payload.dj_id,
        organisator_id=current.id,
    )
    db.add(ev)
    await db.commit()
    await db.refresh(ev)
    return ev

@app.get("/organisator/events/{event_id}", response_model=EventOut)
async def get_event_ep(
        event_id: int,
        db: AsyncSession = Depends(get_db),
        current=Depends(get_current_organisator),
):
    ev = await db.get(Event, event_id)
    if not ev or ev.organisator_id != current.id:
        raise HTTPException(status_code=404, detail="Event not found")
    return ev

@app.delete("/organisator/events/{event_id}", status_code=204)
async def delete_event_ep(
        event_id: int,
        db: AsyncSession = Depends(get_db),
        current=Depends(get_current_organisator),
):
    ev = await db.get(Event, event_id)
    if not ev or ev.organisator_id != current.id:
        raise HTTPException(status_code=404, detail="Event not found")
    await db.delete(ev)
    await db.commit()
    return Response(status_code=204)


# ---------- DEV: init DB ----------
# Ти просив GET — залишаю GET, щоб не ловити 405 під час тесту
@app.get("/__dev__/init_db")
async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    return {"created": True}


# ---------- ADMIN (WEBAPP) з Telegram guard ----------
# Якщо хочеш використовувати Telegram WebApp initData замість jwt-кукі:
async def require_org(request: Request, db: AsyncSession = Depends(get_db)) -> Organisator:
    init_data = request.headers.get("X-Telegram-InitData") or request.cookies.get("tg_init")
    if not init_data:
        raise HTTPException(status_code=401, detail="Telegram auth required")
    user = verify_telegram_init_data(init_data)  # очікується dict з {"id": <telegram_user_id>, ...}
    q = select(Organisator).where(Organisator.telegram_id == user["id"])
    org = (await db.execute(q)).scalar_one_or_none()
    if not org:
        raise HTTPException(status_code=403, detail="Organizer role required")
    return org

@app.get("/admin", response_class=HTMLResponse)
async def admin_dashboard(
        request: Request,
        org: Organisator = Depends(require_org),
        db: AsyncSession = Depends(get_db),
):
    club = (await db.execute(select(Club).where(Club.id == org.club_id))).scalar_one()
    events = (
        await db.execute(
            select(Event)
            .where(Event.club_id == club.id)
            .order_by(desc(Event.start_date).nullslast())
        )
    ).scalars().all()
    return templates.TemplateResponse(
        "admin_dashboard.html",
        {"request": request, "org": org, "club": club, "events": events},
    )

@app.get("/admin/events/new", response_class=HTMLResponse)
async def admin_new_event_form(
        request: Request,
        org: Organisator = Depends(require_org),
        db: AsyncSession = Depends(get_db),
):
    club = (await db.execute(select(Club).where(Club.id == org.club_id))).scalar_one()
    return templates.TemplateResponse("admin_event_new.html", {"request": request, "club": club})

@app.post("/admin/events/new")
async def admin_create_event(
        request: Request,
        title: str = Form(...),
        preview: str = Form(""),
        start_date: str = Form(""),
        db: AsyncSession = Depends(get_db),
        org: Organisator = Depends(require_org),
):
    # Підлаштуй під свою EventCreate (тип start_date може бути datetime)
    payload = EventCreate(
        title=title,
        preview=preview or None,
        start_date=start_date or None,
    )
    data = payload.model_dump(exclude_unset=True)
    data["organisator_id"] = org.id
    data["club_id"] = org.club_id  # якщо твоя схема/CRUD це очікує
    ev = Event(**{k: v for k, v in data.items() if hasattr(Event, k)})
    db.add(ev)
    await db.commit()
    await db.refresh(ev)
    return RedirectResponse(url="/admin", status_code=303)
