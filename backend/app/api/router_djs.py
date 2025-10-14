from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.session import get_async_session
from app.crud.dj_crud import list_all, create, get_by_telegram
from pydantic import BaseModel

router = APIRouter(prefix="/api/v1/djs", tags=["djs"])

class DjCreateBody(BaseModel):
    name: str
    telegram_id: int

@router.get("/")
async def list_djs(db: AsyncSession = Depends(get_async_session)):
    return await list_all(db)

@router.post("/")
async def create_dj(body: DjCreateBody, db: AsyncSession = Depends(get_async_session)):
    return await create(db, body)

@router.get("/by-telegram/{telegram_id}")
async def get_dj_by_tg(telegram_id: int, db: AsyncSession = Depends(get_async_session)):
    return await get_by_telegram(db, telegram_id)
