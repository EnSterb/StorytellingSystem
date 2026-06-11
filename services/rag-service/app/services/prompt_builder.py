from app.models.chunk import Chunk


class PromptBuilder:
    def build(self, query: str, chunks: list[Chunk]) -> str:
        if not chunks:
            context = "Контекст не найден."
        else:
            parts = [f"[{i}] ({chunk.doc_type}) {chunk.content}"
                     for i, chunk in enumerate(chunks, 1)]
            context = "\n\n".join(parts)

        return (
            f"Ты — помощник по созданию историй. "
            f"Используй только следующий контекст для ответа.\n\n"
            f"=== КОНТЕКСТ ===\n{context}"
        )

