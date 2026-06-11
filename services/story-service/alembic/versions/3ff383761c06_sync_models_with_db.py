"""sync models with db

Revision ID: 3ff383761c06
Revises: 3d59ee7363ca
Create Date: 2026-03-20 13:35:36.997603

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3ff383761c06'
down_revision: Union[str, Sequence[str], None] = '3d59ee7363ca'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
