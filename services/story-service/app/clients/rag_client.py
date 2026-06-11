import httpx
from app.core.config import settings


class RagClient:
    def __init__(self):
        self._base_url = settings.RAG_SERVICE_URL
        self._client = httpx.AsyncClient(timeout=60.0)

    async def ingest(
        self,
        document_id: int,
        world_id: int,
        user_id: int,
        doc_type: str,
        content: str,
    ) -> int:
        """Отправить документ на индексацию. Возвращает кол-во чанков."""
        response = await self._client.post(
            f"{self._base_url}/api/v1/ingest",
            json={
                "document_id": document_id,
                "world_id": world_id,
                "user_id": user_id,
                "doc_type": doc_type,
                "content": content,
            },
        )
        response.raise_for_status()
        return response.json()["chunks_created"]

    async def delete_document(self, document_id: int) -> None:
        """Удалить чанки документа из векторного хранилища."""
        await self._client.post(
            f"{self._base_url}/api/v1/ingest",
            json={
                "document_id": document_id,
                "world_id": 0,
                "user_id": 0,
                "doc_type": "deleted",
                "content": "",   # пустой контент → ingest удалит старые чанки и не создаст новых
            },
        )

    async def aclose(self) -> None:
        await self._client.aclose()

    async def retrieve_context(self, query, world_id, top_k=5) -> tuple[str, list[int]]:
        """Получить RAG-промпт для запроса пользователя."""
        response = await self._client.post(
            f"{self._base_url}/api/v1/retrieve-context",
            json={
                "query": query,
                "world_id": world_id,
                "top_k": top_k,
            },
        )
        response.raise_for_status()
        data = response.json()
        return data["prompt"], data.get("chunk_ids", [])
