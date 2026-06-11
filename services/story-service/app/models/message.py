from sqlalchemy import Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Enum as SAEnum
import enum
from .base import Base, TimestampMixin

class RoleEnum(str, enum.Enum):
    user      = "user"
    assistant = "assistant"
    system    = "system"

class Message(Base, TimestampMixin):
    __tablename__ = "messages"

    id: Mapped[int] = mapped_column(primary_key=True)
    session_id: Mapped[int] = mapped_column(
        ForeignKey("sessions.id", ondelete="CASCADE"), nullable=False
    )
    role: Mapped[RoleEnum] = mapped_column(SAEnum(RoleEnum), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    used_chunks: Mapped[str] = mapped_column(Text, nullable=True)

    session: Mapped["Session"] = relationship(back_populates="messages")
