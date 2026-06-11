from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.document import Document
from app.repositories.base import BaseRepository


class DocumentRepository(BaseRepository[Document]):

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(Document, session)

    async def get_by_world_id(
        self, world_id: int, limit: int = 20, offset: int = 0
    ) -> list[Document]:
        result = await self._session.execute(
            select(Document)
            .where(Document.world_id == world_id)
            .order_by(Document.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return list(result.scalars().all())

    async def count_by_world(self, world_id: int) -> int:
        result = await self._session.execute(
            select(func.count())
            .select_from(Document)
            .where(Document.world_id == world_id)
        )
        return result.scalar_one()

    async def mark_indexed(self, document_id: int) -> Document | None:
        return await self.update(document_id, is_indexed=True)

    async def get_unindexed_by_world(self, world_id: int) -> list[Document]:
        result = await self._session.execute(
            select(Document)
            .where(Document.world_id == world_id, Document.is_indexed.is_(False))
            .order_by(Document.created_at.desc())
        )
        return list(result.scalars().all())