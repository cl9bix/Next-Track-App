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
from app.api.router_admin import router as admin_router

app = FastAPI(title="Next Track API")

ALLOWED_ORIGINS = [
    "http://localhost:5500",
    "http://127.0.0.1:5500",
    "https://next-track.fun",
    "https://www.next-track.fun",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("user.html", {"request": request})

@app.get("/health")
async def health():
    return {"status": "ok"}

# API routers
app.include_router(search_router)
app.include_router(tg_auth_router)
app.include_router(events_router)
app.include_router(ws_router)
app.include_router(admin_router)

@app.get("/__dev__/init_db")
async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    return {"created": True}

@app.on_event("shutdown")
async def _shutdown():
    await close_http_client()
