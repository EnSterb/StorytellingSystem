from datetime import datetime
from pydantic import BaseModel, field_validator


class WorldCreate(BaseModel):
    name: str
    description: str | None = None

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        v = v.strip()
        if len(v) < 2 or len(v) > 256:
            raise ValueError("World name must be between 2 and 256 characters")
        return v


class WorldResponse(BaseModel):
    id: int
    owner_id: int
    name: str
    description: str | None
    created_at: datetime

    model_config = {"from_attributes": True}
