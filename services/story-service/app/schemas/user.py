from datetime import datetime
from pydantic import BaseModel, EmailStr, field_validator
import re


class UserResponse(BaseModel):
    id: int
    username: str
    email: EmailStr
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class UserUpdate(BaseModel):
    username: str | None = None
    email: EmailStr | None = None

    @field_validator("username")
    @classmethod
    def validate_username(cls, v: str | None) -> str | None:
        if v is not None:
            v = v.strip()
            if len(v) < 3 or len(v) > 64:
                raise ValueError("Username must be between 3 and 64 characters")
            if not re.match(r"^[a-zA-Z0-9_-]+$", v):
                raise ValueError("Username can only contain letters, numbers, _ and -")
        return v
