from datetime import datetime
from pydantic import BaseModel, field_validator

from app.models.message import RoleEnum


class MessageCreate(BaseModel):
    session_id: int
    role: RoleEnum
    content: str

    @field_validator("content")
    @classmethod
    def validate_content(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Message content cannot be empty")
        if len(v) > 10_000:
            raise ValueError("Message content too long (max 10000 chars)")
        return v


class MessageResponse(BaseModel):
    id: int
    session_id: int
    role: RoleEnum
    content: str
    created_at: datetime

    model_config = {"from_attributes": True}
