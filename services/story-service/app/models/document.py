from sqlalchemy import String, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Enum as SAEnum
import enum
from .base import Base, TimestampMixin

class DocTypeEnum(str, enum.Enum):
    character = "character"
    location  = "location"
    event     = "event"
    rule      = "rule"
    other     = "other"

class Document(Base, TimestampMixin):
    __tablename__ = "documents"

    id: Mapped[int]         = mapped_column(primary_key=True)
    world_id: Mapped[int]   = mapped_column(
        ForeignKey("worlds.id", ondelete="CASCADE"), nullable=False
    )
    title: Mapped[str]      = mapped_column(String(256), nullable=False)
    content: Mapped[str]    = mapped_column(Text, nullable=False)
    doc_type: Mapped[DocTypeEnum] = mapped_column(SAEnum(DocTypeEnum), nullable=False)
    is_indexed: Mapped[bool] = mapped_column(default=False)

    world: Mapped["World"] = relationship(back_populates="documents")

