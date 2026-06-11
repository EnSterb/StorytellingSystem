from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from pgvector.sqlalchemy import Vector
from app.models.chunk import Chunk
from app.core.config import settings


class ChunkRepository:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def add_many(self, chunks: list[Chunk]) -> None:
        """Добавить пачку чанков"""
        self._session.add_all(chunks)
        await self._session.flush()

    async def delete_by_document(self, document_id: int) -> None:
        """Удалить все чанки документа (при переиндексации)"""
        await self._session.execute(
            delete(Chunk).where(Chunk.document_id == document_id)
        )

    async def search_similar(
        self,
        query_vector: list[float],
        world_id: int,
        top_k: int = 5,
    ) -> list[Chunk]:
        """
        Найти top_k чанков ближайших к query_vector
        внутри конкретного мира (world_id)
        """
        result = await self._session.execute(
            select(Chunk)
            .where(Chunk.world_id == world_id)
            .order_by(
                # cosine_distance — чем меньше, тем похожее
                Chunk.embedding.cosine_distance(query_vector)
            )
            .limit(top_k)
        )
        return list(result.scalars().all())
