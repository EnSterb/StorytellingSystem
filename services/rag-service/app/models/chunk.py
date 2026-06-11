from sqlalchemy import String, Text, Integer, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column
from pgvector.sqlalchemy import Vector

from app.models.base import Base, TimestampMixin
from app.core.config import settings


class Chunk(Base, TimestampMixin):
    __tablename__ = "chunks"

    id:          Mapped[int] = mapped_column(primary_key=True)

    # Откуда пришёл чанк
    document_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    world_id:    Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    user_id:     Mapped[int] = mapped_column(Integer, nullable=False, index=True)

    # Тип документа (character/location/event/rule/other)
    doc_type:    Mapped[str] = mapped_column(String(64), nullable=False)

    # Сам текст чанка
    content:     Mapped[str] = mapped_column(Text, nullable=False)

    # Позиция чанка внутри документа (для контекста)
    chunk_index: Mapped[int] = mapped_column(Integer, nullable=False)

    # Вектор — сердце RAG
    embedding: Mapped[list[float]] = mapped_column(
        Vector(settings.VECTOR_DIM), nullable=False
    )

    __table_args__ = (
        # HNSW индекс — быстрый поиск ближайших векторов
        Index(
            "ix_chunks_embedding_hnsw",
            "embedding",
            postgresql_using="hnsw",
            postgresql_with={"m": 16, "ef_construction": 64},
            postgresql_ops={"embedding": "vector_cosine_ops"}, # косинусное расстояние (стандарт для text embeddings)
        ),
    )
