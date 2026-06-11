from datetime import datetime
from pydantic import BaseModel, field_validator
from app.models.session import SessionModeEnum


class SessionCreate(BaseModel):
    title: str | None = None
    generate_intro: bool = False
    mode: SessionModeEnum = SessionModeEnum.narrator
    character_name: str | None = None

    @field_validator("title")
    @classmethod
    def validate_title(cls, v: str | None) -> str | None:
        if v is not None:
            v = v.strip()
            if len(v) > 256:
                raise ValueError("Title must be at most 256 characters")
        return v


class SessionResponse(BaseModel):
    id: int
    user_id: int
    world_id: int | None
    title: str | None
    summary: str | None
    mode: SessionModeEnum
    character_name: str | None
    created_at: datetime

    model_config = {"from_attributes": True}
