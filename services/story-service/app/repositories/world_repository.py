from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.world import World
from app.repositories.base import BaseRepository


class WorldRepository(BaseRepository[World]):

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(World, session)

    async def get_by_owner_id(
            self, owner_id: int, limit: int = 20, offset: int = 0
    ) -> list[World]:
        result = await self._session.execute(
            select(World)
            .where(World.owner_id == owner_id)
            .limit(limit)
            .offset(offset)
        )
        return list(result.scalars().all())

    async def count_by_owner(self, owner_id: int) -> int:
        result = await self._session.execute(
            select(func.count()).select_from(World).where(World.owner_id == owner_id)
        )
        return result.scalar_one()
