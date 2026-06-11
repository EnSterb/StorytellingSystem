from app.backends.base import LLMBackend


class GenerationService:
    def __init__(self, backend: LLMBackend):
        self._backend = backend

    async def generate(self, system_prompt: str, history: list[dict]) -> str:
        return await self._backend.generate(system_prompt=system_prompt, history=history)

