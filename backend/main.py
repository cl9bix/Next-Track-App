from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from app.services.music_search import close_http_client

from app.models.session import Base, engine
from app.api.auth_telegram_webapp import router as tg_auth_router
from app.api.routes_event_runtime_tg import router as events_router
from app.api.router_search import router as search_router
from app.api.ws import router as ws_router
from app.api.router_admin_panel import router as admin_router

app = FastAPI(title="Next Track API")

# --- CORS (ngrok domain + локалка для дебагу)
ALLOWED_ORIGINS = [
    "https://unsyncopated-shufflingly-gerald.ngrok-free.dev",
    "http://localhost:5500",
    "http://127.0.0.1:5500",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Static + Templates
# Важливо: папки мають існувати на рівні, з якого ти запускаєш uvicorn
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


# --- Pages
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    # templates/user.html
    return templates.TemplateResponse("user.html", {"request": request})

@app.get("/admin/", response_class=HTMLResponse)
async def admin_page(request: Request):
    # templates/user.html
    return templates.TemplateResponse("admin_dashboard.html", {"request": request})


# --- API routers
app.include_router(search_router)

app.include_router(tg_auth_router)
app.include_router(events_router)
app.include_router(ws_router)
app.include_router(admin_router)


# --- DEV init db
@app.get("/__dev__/init_db")
async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    return {"created": True}


@app.on_event("shutdown")
async def _shutdown():
    await close_http_client()
