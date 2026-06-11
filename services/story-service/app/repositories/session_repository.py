from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.session import Session
from app.repositories.base import BaseRepository


class SessionRepository(BaseRepository[Session]):

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(Session, session)

    async def get_by_user_id(
        self, user_id: int, limit: int = 20, offset: int = 0
    ) -> list[Session]:
        result = await self._session.execute(
            select(Session)
            .where(Session.user_id == user_id)
            .order_by(Session.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return list(result.scalars().all())

    async def count_by_user(self, user_id: int) -> int:
        result = await self._session.execute(
            select(func.count()).select_from(Session).where(Session.user_id == user_id)
        )
        return result.scalar_one()

    async def update_summary(self, session_id: int, summary: str) -> Session | None:
        return await self.update(session_id, summary=summary)

    async def get_by_world_id(
            self, world_id: int, user_id: int, limit: int = 100, offset: int = 0
    ) -> list[Session]:
        result = await self._session.execute(
            select(Session)
            .where(Session.world_id == world_id, Session.user_id == user_id)
            .order_by(Session.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return list(result.scalars().all())

    async def count_by_world(self, world_id: int, user_id: int) -> int:
        result = await self._session.execute(
            select(func.count())
            .select_from(Session)
            .where(Session.world_id == world_id, Session.user_id == user_id)
        )
        return result.scalar_one()

