from datetime import datetime
from pydantic import BaseModel, field_validator

from app.models.document import DocTypeEnum


class DocumentCreate(BaseModel):
    title: str
    content: str
    doc_type: DocTypeEnum

    @field_validator("title")
    @classmethod
    def validate_title(cls, v: str) -> str:
        v = v.strip()
        if len(v) < 2 or len(v) > 256:
            raise ValueError("Title must be between 2 and 256 characters")
        return v

    @field_validator("content")
    @classmethod
    def validate_content(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Content cannot be empty")
        if len(v) > 50_000:
            raise ValueError("Content too long (max 50000 chars)")
        return v


class DocumentUpdate(BaseModel):
    title: str | None = None
    content: str | None = None
    doc_type: DocTypeEnum | None = None

    @field_validator("title")
    @classmethod
    def validate_title(cls, v: str | None) -> str | None:
        if v is not None:
            v = v.strip()
            if len(v) < 2 or len(v) > 256:
                raise ValueError("Title must be between 2 and 256 characters")
        return v

    @field_validator("content")
    @classmethod
    def validate_content(cls, v: str | None) -> str | None:
        if v is not None:
            v = v.strip()
            if not v:
                raise ValueError("Content cannot be empty")
            if len(v) > 50_000:
                raise ValueError("Content too long (max 50000 chars)")
        return v


class DocumentResponse(BaseModel):
    id: int
    world_id: int
    title: str
    content: str
    doc_type: DocTypeEnum
    is_indexed: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
