from openai import AsyncOpenAI
from app.backends.base import LLMBackend
from app.core.config import settings


class OpenAIBackend(LLMBackend):
    def __init__(self):
        self._client = AsyncOpenAI(
            base_url=settings.LLM_BASE_URL,
            api_key=settings.LLM_API_KEY,
        )

    async def generate(self, system_prompt: str, history: list[dict]) -> str:
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages += [{"role": m["role"], "content": m["content"]} for m in history]

        response = await self._client.chat.completions.create(
            model=settings.LLM_MODEL,
            messages=messages,
            max_tokens=settings.LLM_MAX_TOKENS,
            temperature=settings.LLM_TEMPERATURE,
        )
        return response.choices[0].message.content or ""


