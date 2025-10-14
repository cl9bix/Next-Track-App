from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter

from app.models.session import get_async_session
from app.crud import organisator_crud
from app.schemas.schemas import OrganisatorCreate, OrganisatorResponse

router = APIRouter()


@router.post("/", response_model=OrganisatorResponse, status_code=201)
async def create_organisator(payload: OrganisatorCreate, db: AsyncSession = Depends(get_async_session)):
    return await organisator_crud.create_organisator(db, payload)


@router.get('/all', response_model=OrganisatorResponse, status_code=200)
async def all_organisators(db: AsyncSession = Depends(get_async_session)):
    return await organisator_crud.get_all_organisators(db)
