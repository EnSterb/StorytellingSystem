import httpx
from app.core.config import settings


class LLMClient:
    def __init__(self):
        self._base_url = settings.LLM_SERVICE_URL
        self._client = httpx.AsyncClient(timeout=600.0)

    async def generate(
        self,
        system_prompt: str,
        history: list[dict],
    ) -> str:
        response = await self._client.post(
            f"{self._base_url}/api/v1/generate",
            json={
                "system_prompt": system_prompt,
                "history": history,
            },
        )
        response.raise_for_status()
        return response.json()["text"]

    async def aclose(self) -> None:
        await self._client.aclose()
