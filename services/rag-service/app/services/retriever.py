from app.models.chunk import Chunk
from app.repositories.chunk_repository import ChunkRepository
from app.embeddings.model import EmbeddingModel


class RetrieverService:
    def __init__(self, repo: ChunkRepository, embedding_model: EmbeddingModel):
        self._repo = repo
        self._model = embedding_model

    async def retrieve(
        self,
        query: str,
        world_id: int,
        top_k: int = 5,
    ) -> list[Chunk]:
        """
        Кодируем вопрос → ищем похожие чанки в векторном пространстве
        """
        query_vector = self._model.encode(query)
        return await self._repo.search_similar(
            query_vector=query_vector,
            world_id=world_id,
            top_k=top_k,
        )
