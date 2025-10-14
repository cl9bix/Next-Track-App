from fastapi import FastAPI
from app.models.session import Base, engine
from app.api.router_public import router as public_router
from app.api.router_organizer import router as organizer_router
from app.api.router_events import router as events_router
from app.api.router_rounds import router as rounds_router
from app.api.router_songs import router as songs_router
from app.api.router_users import router as users_router
from app.api.router_djs import router as djs_router
from app.api.router_ws import router as ws_router

app = FastAPI(title="Next Track API")

app.include_router(public_router)
app.include_router(organizer_router)
app.include_router(events_router)
app.include_router(rounds_router)
app.include_router(songs_router)
app.include_router(users_router)
app.include_router(djs_router)
app.include_router(ws_router)

@app.get("/")
async def root():
    return {"ok": True}

# Dev-only init
@app.post("/__dev__/init_db")
async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    return {"created": True}
