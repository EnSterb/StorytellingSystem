from fastapi import HTTPException, status

from app.models.world import World
from app.repositories.world_repository import WorldRepository


class WorldService:

    def __init__(self, world_repository: WorldRepository) -> None:
        self._world_repo = world_repository

    async def create_world(
        self,
        owner_id: int,
        name: str,
        description: str | None = None,
    ) -> World:
        return await self._world_repo.create(
            owner_id=owner_id,
            name=name,
            description=description,
        )

    async def get_world(self, world_id: int, owner_id: int) -> World:
        world = await self._world_repo.get_by_id(world_id)
        if not world or world.owner_id != owner_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="World not found",
            )
        return world

    async def get_user_worlds(
            self, owner_id: int, limit: int = 20, offset: int = 0
    ) -> list[World]:
        return await self._world_repo.get_by_owner_id(owner_id, limit=limit, offset=offset)

    async def count_user_worlds(self, owner_id: int) -> int:
        return await self._world_repo.count_by_owner(owner_id)

    async def delete_world(self, world_id: int, owner_id: int) -> None:
        world = await self.get_world(world_id, owner_id)
        await self._world_repo.delete(world.id)
