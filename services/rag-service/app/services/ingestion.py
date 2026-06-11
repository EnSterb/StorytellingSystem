from app.models.chunk import Chunk
from app.repositories.chunk_repository import ChunkRepository
from app.embeddings.model import EmbeddingModel


class IngestionService:
    def __init__(self, repo: ChunkRepository, embedding_model: EmbeddingModel):
        self._repo = repo
        self._model = embedding_model

    async def ingest_document(
        self,
        document_id: int,
        world_id: int,
        user_id: int,
        doc_type: str,
        content: str,
    ) -> int:
        """
        Принимает сырой текст документа,
        нарезает на чанки, кодирует, сохраняет.
        Возвращает количество созданных чанков.
        """
        # Удаляем старые чанки если документ переиндексируется
        await self._repo.delete_by_document(document_id)

        # Нарезаем текст
        chunks_text = self._split_text(content)

        # Кодируем всё пачкой — быстрее чем по одному
        vectors = self._model.encode_batch(chunks_text)

        # Собираем ORM объекты
        chunks = [
            Chunk(
                document_id=document_id,
                world_id=world_id,
                user_id=user_id,
                doc_type=doc_type,
                content=text,
                chunk_index=i,
                embedding=vector,
            )
            for i, (text, vector) in enumerate(zip(chunks_text, vectors))
        ]

        await self._repo.add_many(chunks)
        return len(chunks)

    def _split_text(self, text: str, chunk_size: int = 512, overlap: int = 50) -> list[str]:
        """
        Нарезка текста на чанки с перекрытием.

        Пример с chunk_size=20, overlap=5:
        "AAAAABBBBBCCCCCDDDDD"
         [AAAAABBBBBCCCCC]       chunk 0 (0..15)
               [BBBBBCCCCCDDDD]  chunk 1 (10..25)  ← перекрытие 5 символов
        """
        if len(text) <= chunk_size:
            return [text]

        chunks = []
        start = 0
        while start < len(text):
            end = start + chunk_size
            chunks.append(text[start:end])
            start += chunk_size - overlap  # сдвигаемся с учётом overlap

        return chunks
