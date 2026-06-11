from sentence_transformers import SentenceTransformer
import numpy as np
from app.core.config import settings


class EmbeddingModel:
    def __init__(self):
        # Загружаем модель один раз при старте сервиса
        self._model = SentenceTransformer(settings.EMBEDDING_MODEL)

    def encode(self, text: str) -> list[float]:
        """Один текст → вектор"""
        vector: np.ndarray = self._model.encode(text, normalize_embeddings=True)
        return vector.tolist()

    def encode_batch(self, texts: list[str]) -> list[list[float]]:
        """Много текстов → много векторов (быстрее чем по одному)"""
        vectors: np.ndarray = self._model.encode(
            texts,
            normalize_embeddings=True,
            batch_size=32,
            show_progress_bar=False,
        )
        return vectors.tolist()
