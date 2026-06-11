from typing import Union, Sequence

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'd69f1870d584'
down_revision: Union[str, Sequence[str], None] = '3ff383761c06'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 1. Создаём тип enum для session_mode
    sessionmode_enum = postgresql.ENUM(
        "narrator",
        "player",
        name="sessionmodeenum",
    )
    sessionmode_enum.create(op.get_bind(), checkfirst=True)

    # 2. Добавляем столбец mode с default='narrator'
    op.add_column(
        "sessions",
        sa.Column(
            "mode",
            sessionmode_enum,
            nullable=False,
            server_default="narrator",
        ),
    )

    # 3. Добавляем character_name (может быть NULL)
    op.add_column(
        "sessions",
        sa.Column("character_name", sa.String(length=128), nullable=True),
    )

    # 4. Убираем server_default, чтобы в модели работал python‑default
    op.alter_column("sessions", "mode", server_default=None)


def downgrade() -> None:
    # 1. Удаляем столбцы
    op.drop_column("sessions", "character_name")
    op.drop_column("sessions", "mode")

    # 2. Удаляем enum тип
    sessionmode_enum = postgresql.ENUM(
        "narrator",
        "player",
        name="sessionmodeenum",
    )
    sessionmode_enum.drop(op.get_bind(), checkfirst=True)
