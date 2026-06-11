from abc import ABC, abstractmethod


class LLMBackend(ABC):
    @abstractmethod
    async def generate(self, prompt: str) -> str:
        """Принимает промпт → возвращает сгенерированный текст"""
        ...
