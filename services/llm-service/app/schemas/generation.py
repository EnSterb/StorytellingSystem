from pydantic import BaseModel


class Message(BaseModel):
    role: str  # "user" | "assistant"
    content: str


class GenerateRequest(BaseModel):
    system_prompt: str = ""
    history: list[Message] = []


class GenerateResponse(BaseModel):
    text: str
