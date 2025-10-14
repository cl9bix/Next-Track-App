from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.session import get_async_session
from app.crud.round_crud import list_rounds, get_round, set_current_round
from app.schemas.schemas import RoundResponse

router = APIRouter(prefix="/api/v1/rounds", tags=["rounds"])

@router.get("/event/{event_id}", response_model=list[RoundResponse])
async def list_rounds_ep(event_id: int, db: AsyncSession = Depends(get_async_session)):
    return await list_rounds(db, event_id)

@router.get("/{round_id}", response_model=RoundResponse)
async def get_round_ep(round_id: int, db: AsyncSession = Depends(get_async_session)):
    return await get_round(db, round_id)

# адміністратор/організатор — зроби захист так само, як у organizer router, якщо потрібно
