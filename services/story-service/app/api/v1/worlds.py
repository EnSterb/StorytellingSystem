from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_db_session
from app.core.dependencies import get_current_user
from app.models.user import User
from app.repositories.world_repository import WorldRepository
from app.schemas import WorldCreate, WorldResponse
from app.services.world_service import WorldService

router = APIRouter(prefix="/worlds", tags=["worlds"])


def get_world_service(db: AsyncSession = Depends(get_db_session)) -> WorldService:
    return WorldService(WorldRepository(db))


@router.post("", response_model=WorldResponse, status_code=201)
async def create_world(
    body: WorldCreate,
    current_user: User = Depends(get_current_user),
    service: WorldService = Depends(get_world_service),
):
    return await service.create_world(
        owner_id=current_user.id,
        name=body.name,
        description=body.description,
    )


@router.get("", response_model=list[WorldResponse])
async def get_worlds(
    current_user: User = Depends(get_current_user),
    service: WorldService = Depends(get_world_service),
):
    return await service.get_user_worlds(current_user.id)


@router.get("/{world_id}", response_model=WorldResponse)
async def get_world(
    world_id: int,
    current_user: User = Depends(get_current_user),
    service: WorldService = Depends(get_world_service),
):
    return await service.get_world(world_id, current_user.id)


@router.delete("/{world_id}", status_code=204)
async def delete_world(
    world_id: int,
    current_user: User = Depends(get_current_user),
    service: WorldService = Depends(get_world_service),
):
    await service.delete_world(world_id, current_user.id)
