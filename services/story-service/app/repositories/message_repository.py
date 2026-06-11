from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.message import Message, RoleEnum
from app.repositories.base import BaseRepository


class MessageRepository(BaseRepository[Message]):

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(Message, session)

    async def get_by_session_id(self, session_id: int) -> list[Message]:
        result = await self._session.execute(
            select(Message)
            .where(Message.session_id == session_id)
            .order_by(Message.created_at)
        )
        return list(result.scalars().all())

    async def count_by_session(self, session_id: int) -> int:
        result = await self._session.execute(
            select(func.count()).where(Message.session_id == session_id)
        )
        return result.scalar_one()

    async def get_last_n(self, session_id: int, n: int = 10) -> list[Message]:
        result = await self._session.execute(
            select(Message)
            .where(Message.session_id == session_id)
            .order_by(Message.created_at.desc())
            .limit(n)
        )
        return list(reversed(result.scalars().all()))
