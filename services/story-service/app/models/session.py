import enum

from sqlalchemy import String, Text, ForeignKey
from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base, TimestampMixin

class SessionModeEnum(str, enum.Enum):
    narrator = "narrator"   # текущий режим
    player   = "player"     # dungeon-режим

class Session(Base, TimestampMixin):
    __tablename__ = "sessions"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    title: Mapped[str] = mapped_column(String(256), nullable=True)
    summary: Mapped[str] = mapped_column(Text, nullable=True)
    world_id: Mapped[int] = mapped_column(
        ForeignKey("worlds.id", ondelete="CASCADE"), nullable=True
    )
    mode: Mapped[SessionModeEnum] = mapped_column(
        SAEnum(SessionModeEnum),
        default=SessionModeEnum.narrator,
        nullable=False,
    )
    character_name: Mapped[str | None] = mapped_column(String(128), nullable=True)

    user: Mapped["User"] = relationship(back_populates="sessions")
    messages: Mapped[list["Message"]] = relationship(
        back_populates="session",
        cascade="all, delete-orphan",
    )
    world: Mapped["World"] = relationship(back_populates="sessions")
