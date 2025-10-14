from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.session import get_async_session
from app.crud.user_crud import list_users, get_user, set_notifications
from pydantic import BaseModel

router = APIRouter(prefix="/api/v1/users", tags=["users"])

class ToggleNotif(BaseModel):
    enabled: bool

@router.get("/", response_model=list)
async def list_users_ep(db: AsyncSession = Depends(get_async_session)):
    return await list_users(db)

@router.get("/{user_id}")
async def get_user_ep(user_id: int, db: AsyncSession = Depends(get_async_session)):
    return await get_user(db, user_id)

@router.post("/{user_id}/notifications")
async def toggle_notif(user_id: int, body: ToggleNotif, db: AsyncSession = Depends(get_async_session)):
    return await set_notifications(db, user_id, body.enabled)
